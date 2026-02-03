"""
D38999 Connector Specification Parser
Parses MIL-DTL-38999 part numbers and returns detailed specifications
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Contact:
    """Individual contact specification"""
    position: str  # e.g., "A", "B", "1", "2"
    size: int  # 20, 16, 12, 8, 4
    x: float  # mm from center
    y: float  # mm from center
    type: str  # "Socket" or "Pin"
    wire_gauge: str  # e.g., "20-24 AWG"
    current_rating: float  # Amperes
    crimp_tool: str  # Tool part number
    extraction_tool: str  # Extraction tool part number
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class Dimension:
    """Connector dimension specification"""
    name: str
    value: float  # mm
    tolerance: float  # mm
    reference: str  # Drawing reference
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ConnectorSpecs:
    """Complete connector specifications"""
    part_number: str
    series: str
    shell_size: int
    insert_arrangement: str
    contacts: List[Contact] = field(default_factory=list)
    dimensions: List[Dimension] = field(default_factory=list)
    assembly_tooling: List[str] = field(default_factory=list)
    voltage_rating: Dict[str, float] = field(default_factory=dict)
    environmental_specs: Dict = field(default_factory=dict)
    mechanical_specs: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'part_number': self.part_number,
            'series': self.series,
            'shell_size': self.shell_size,
            'insert_arrangement': self.insert_arrangement,
            'contacts': [contact.to_dict() for contact in self.contacts],
            'dimensions': [dim.to_dict() for dim in self.dimensions],
            'assembly_tooling': self.assembly_tooling,
            'voltage_rating': self.voltage_rating,
            'environmental_specs': self.environmental_specs,
            'mechanical_specs': self.mechanical_specs
        }


class D38999Specs:
    """
    Parser for D38999 connector specifications
    
    Part Number Format: D38999/24ZA98SN
    - D38999: Specification
    - 24: Shell size
    - Z: Series indicator
    - A: Insert arrangement class
    - 98: Insert arrangement number
    - S: Shell style (Socket)
    - N: Contact type/finish
    """
    
    # Contact size specifications
    CONTACT_SPECS = {
        4: {
            "wire_gauge": "4-8 AWG",
            "current_rating": 75.0,
            "crimp_tool": "M22520/5-01",
            "extraction_tool": "M81969/14-01"
        },
        8: {
            "wire_gauge": "8-12 AWG",
            "current_rating": 46.0,
            "crimp_tool": "M22520/5-01",
            "extraction_tool": "M81969/14-02"
        },
        12: {
            "wire_gauge": "12-16 AWG",
            "current_rating": 23.0,
            "crimp_tool": "M22520/2-01",
            "extraction_tool": "M81969/14-03"
        },
        16: {
            "wire_gauge": "16-20 AWG",
            "current_rating": 13.0,
            "crimp_tool": "M22520/2-01",
            "extraction_tool": "M81969/14-04"
        },
        20: {
            "wire_gauge": "20-24 AWG",
            "current_rating": 7.5,
            "crimp_tool": "M22520/2-01",
            "extraction_tool": "M81969/14-05"
        },
        22: {
            "wire_gauge": "22-26 AWG",
            "current_rating": 5.0,
            "crimp_tool": "M22520/2-01",
            "extraction_tool": "M81969/14-06"
        }
    }
    
    # Series definitions
    SERIES = {
        'W': 'Series I - Bayonet Coupling',
        'T': 'Series II - Threaded Coupling',
        'Z': 'Series III - Breech Coupling',
        'H': 'Series IV - Hermetic Solder'
    }
    
    # Insert arrangements (sample - would need complete database)
    # Format: shell_size -> arrangement_code -> contact_layout
    INSERT_ARRANGEMENTS = {
        24: {
            'A98': {
                'contacts': [
                    {'pos': 'A', 'size': 16, 'angle': 0, 'radius': 9.5},
                    {'pos': 'B', 'size': 16, 'angle': 45, 'radius': 9.5},
                    {'pos': 'C', 'size': 16, 'angle': 90, 'radius': 9.5},
                    {'pos': 'D', 'size': 16, 'angle': 135, 'radius': 9.5},
                    {'pos': 'E', 'size': 16, 'angle': 180, 'radius': 9.5},
                    {'pos': 'F', 'size': 16, 'angle': 225, 'radius': 9.5},
                    {'pos': 'G', 'size': 16, 'angle': 270, 'radius': 9.5},
                    {'pos': 'H', 'size': 16, 'angle': 315, 'radius': 9.5},
                    {'pos': '1', 'size': 20, 'angle': 22.5, 'radius': 6.5},
                    {'pos': '2', 'size': 20, 'angle': 67.5, 'radius': 6.5},
                    {'pos': '3', 'size': 20, 'angle': 112.5, 'radius': 6.5},
                    {'pos': '4', 'size': 20, 'angle': 157.5, 'radius': 6.5},
                    {'pos': '5', 'size': 20, 'angle': 202.5, 'radius': 6.5},
                    {'pos': '6', 'size': 20, 'angle': 247.5, 'radius': 6.5},
                    {'pos': '7', 'size': 20, 'angle': 292.5, 'radius': 6.5},
                    {'pos': '8', 'size': 20, 'angle': 337.5, 'radius': 6.5},
                ]
            }
        }
    }
    
    def __init__(self):
        self.environmental_specs = {
            "operating_temp_min": -65,  # °C
            "operating_temp_max": 200,  # °C
            "storage_temp_min": -67,  # °C
            "storage_temp_max": 200,  # °C
            "humidity": 95,  # % RH
            "altitude_max": 21336,  # meters (70,000 feet)
            "vibration_freq_min": 10,  # Hz
            "vibration_freq_max": 2000,  # Hz
            "shock": 100,  # G
            "salt_spray_hours": 48,
            "ip_rating": "IP67"
        }
        
        self.mechanical_specs = {
            "mating_cycles_min": 500,
            "mating_cycles_high_perf": 1000,
            "engagement_rotation_bayonet": 90,  # degrees
            "engagement_rotation_breech": 45,  # degrees
        }
    
    def parse_part_number(self, part_number: str) -> ConnectorSpecs:
        """
        Parse a D38999 part number and return complete specifications
        
        Args:
            part_number: D38999 format part number (e.g., "D38999/24ZA98SN")
            
        Returns:
            ConnectorSpecs object with all specifications
        """
        # Remove spaces and convert to uppercase
        part_number = part_number.replace(" ", "").upper()
        
        # Parse the part number
        # Format: D38999/[shell_size][series][insert_arrangement][shell_style][options]
        parts = part_number.split('/')
        if len(parts) != 2 or not parts[0].startswith('D38999'):
            raise ValueError(f"Invalid part number format: {part_number}")
        
        descriptor = parts[1]
        
        # Extract shell size (first 2 digits)
        shell_size = int(descriptor[:2])
        
        # Extract series (next character)
        series_code = descriptor[2]
        series = self.SERIES.get(series_code, f"Unknown Series ({series_code})")
        
        # Extract insert arrangement (next 3 characters typically)
        # This varies, but commonly it's a letter + 2 digits
        insert_arrangement = descriptor[3:6]
        
        # Extract shell style (next character)
        shell_style_code = descriptor[6] if len(descriptor) > 6 else 'S'
        shell_style = 'Socket' if shell_style_code == 'S' else 'Pin'
        
        # Create specs object
        specs = ConnectorSpecs(
            part_number=part_number,
            series=series,
            shell_size=shell_size,
            insert_arrangement=insert_arrangement
        )
        
        # Get contact layout
        specs.contacts = self._get_contacts(shell_size, insert_arrangement, shell_style)
        
        # Get dimensions
        specs.dimensions = self._get_dimensions(shell_size, series_code)
        
        # Get assembly tooling
        specs.assembly_tooling = self._get_assembly_tooling(specs.contacts, series_code)
        
        # Get voltage rating
        specs.voltage_rating = self._get_voltage_rating(shell_size)
        
        # Add environmental and mechanical specs
        specs.environmental_specs = self.environmental_specs.copy()
        specs.mechanical_specs = self.mechanical_specs.copy()
        
        return specs
    
    def _get_contacts(self, shell_size: int, arrangement: str, shell_style: str) -> List[Contact]:
        """Generate contact list based on insert arrangement"""
        contacts = []
        
        # Get contact layout from database
        layout = self.INSERT_ARRANGEMENTS.get(shell_size, {}).get(arrangement, {}).get('contacts', [])
        
        if not layout:
            # If arrangement not in database, return placeholder
            print(f"Warning: Insert arrangement {arrangement} for shell size {shell_size} not in database")
            return []
        
        contact_type = "Socket" if shell_style == 'S' else "Pin"
        
        for contact_def in layout:
            # Convert polar to cartesian coordinates
            angle_rad = math.radians(contact_def['angle'])
            x = contact_def['radius'] * math.cos(angle_rad)
            y = contact_def['radius'] * math.sin(angle_rad)
            
            size = contact_def['size']
            spec = self.CONTACT_SPECS[size]
            
            contact = Contact(
                position=contact_def['pos'],
                size=size,
                x=round(x, 2),
                y=round(y, 2),
                type=contact_type,
                wire_gauge=spec['wire_gauge'],
                current_rating=spec['current_rating'],
                crimp_tool=spec['crimp_tool'],
                extraction_tool=spec['extraction_tool']
            )
            contacts.append(contact)
        
        return contacts
    
    def _get_dimensions(self, shell_size: int, series_code: str) -> List[Dimension]:
        """Get critical dimensions for the connector"""
        # Shell size in 1/16 inch increments, converted to mm
        shell_od = (shell_size / 16) * 25.4
        
        dimensions = [
            Dimension("Shell OD", shell_od, 0.25, "MS27473"),
            Dimension("Thread Major Dia", shell_od - 1.5, 0.15, "MS27473"),
            Dimension("Flange OD", shell_od + 6.0, 0.30, "MS27473"),
            Dimension("Flange Thickness", 2.0, 0.1, "MS27473"),
            Dimension("Shell Length", 25.0 + (shell_size * 0.5), 0.5, "MS27473"),
            Dimension("Pin Depth", 8.0, 0.2, "MS27473"),
            Dimension("Bayonet Pin Height", 1.5, 0.1, "MS27473") if series_code == 'W' else None,
            Dimension("Thread Length", 12.0, 0.3, "MS27473") if series_code == 'T' else None,
        ]
        
        # Filter out None values
        return [d for d in dimensions if d is not None]
    
    def _get_assembly_tooling(self, contacts: List[Contact], series_code: str) -> List[str]:
        """Get required tooling for assembly"""
        tools = set()
        
        # Add crimp and extraction tools for each contact size
        for contact in contacts:
            tools.add(contact.crimp_tool)
            tools.add(contact.extraction_tool)
        
        # Add connector-specific tools
        tools.add("Insertion/Extraction Tool Set - M81969/14")
        tools.add("Contact Crimp Tool - M22520/2-01")
        
        if series_code == 'T':
            tools.add("Coupling Nut Wrench")
        
        tools.add("Pin/Socket Gauge - MS27487")
        tools.add("Continuity Tester")
        
        return sorted(list(tools))
    
    def _get_voltage_rating(self, shell_size: int) -> Dict[str, float]:
        """Get voltage ratings"""
        return {
            "sea_level_rms": 600.0,
            "sea_level_dc": 850.0,
            "50000_ft_rms": 150.0,
            "70000_ft_rms": 100.0,
            "dielectric_withstand": 1500.0,
            "insulation_resistance_min": 5000.0  # megohms
        }
    
    def print_specs(self, specs: ConnectorSpecs):
        """Pretty print connector specifications"""
        print(f"\n{'='*80}")
        print(f"D38999 CONNECTOR SPECIFICATIONS")
        print(f"{'='*80}")
        print(f"Part Number: {specs.part_number}")
        print(f"Series: {specs.series}")
        print(f"Shell Size: {specs.shell_size}")
        print(f"Insert Arrangement: {specs.insert_arrangement}")
        
        print(f"\n{'CONTACTS':-^80}")
        print(f"{'Pos':<6} {'Size':<6} {'X(mm)':<8} {'Y(mm)':<8} {'Type':<8} {'Wire Gauge':<12} {'Current(A)':<10} {'Crimp Tool'}")
        print("-" * 80)
        for contact in specs.contacts:
            print(f"{contact.position:<6} {contact.size:<6} {contact.x:<8.2f} {contact.y:<8.2f} "
                  f"{contact.type:<8} {contact.wire_gauge:<12} {contact.current_rating:<10.1f} {contact.crimp_tool}")
        
        print(f"\n{'DIMENSIONS':-^80}")
        print(f"{'Name':<30} {'Value (mm)':<15} {'Tolerance (mm)':<20} {'Reference'}")
        print("-" * 80)
        for dim in specs.dimensions:
            print(f"{dim.name:<30} {dim.value:<15.2f} ±{dim.tolerance:<19.2f} {dim.reference}")
        
        print(f"\n{'ASSEMBLY TOOLING':-^80}")
        for tool in specs.assembly_tooling:
            print(f"  • {tool}")
        
        print(f"\n{'VOLTAGE RATINGS':-^80}")
        for rating, value in specs.voltage_rating.items():
            print(f"  • {rating.replace('_', ' ').title()}: {value} V" if 'megohm' not in rating 
                  else f"  • {rating.replace('_', ' ').title()}: {value} MΩ")
        
        print(f"\n{'ENVIRONMENTAL SPECIFICATIONS':-^80}")
        env = specs.environmental_specs
        print(f"  • Operating Temperature: {env['operating_temp_min']}°C to {env['operating_temp_max']}°C")
        print(f"  • Storage Temperature: {env['storage_temp_min']}°C to {env['storage_temp_max']}°C")
        print(f"  • Humidity: {env['humidity']}% RH")
        print(f"  • Altitude: Up to {env['altitude_max']} meters")
        print(f"  • Vibration: {env['vibration_freq_min']}-{env['vibration_freq_max']} Hz")
        print(f"  • Shock: {env['shock']} G")
        print(f"  • Salt Spray: {env['salt_spray_hours']} hours")
        print(f"  • IP Rating: {env['ip_rating']}")
        
        print(f"\n{'MECHANICAL SPECIFICATIONS':-^80}")
        mech = specs.mechanical_specs
        print(f"  • Mating Cycles (Standard): {mech['mating_cycles_min']}")
        print(f"  • Mating Cycles (High Performance): {mech['mating_cycles_high_perf']}")
        if 'Series I' in specs.series:
            print(f"  • Engagement Rotation: {mech['engagement_rotation_bayonet']}°")
        elif 'Series III' in specs.series:
            print(f"  • Engagement Rotation: {mech['engagement_rotation_breech']}°")
        
        print(f"\n{'='*80}\n")


# Example usage
if __name__ == "__main__":
    parser = D38999Specs()
    
    # Parse the example part number
    specs = parser.parse_part_number("D38999/24ZA98SN")
    
    # Print specifications
    parser.print_specs(specs)
    
    # Access individual components programmatically
    print("\nProgrammatic Access Examples:")
    print(f"Total contacts: {len(specs.contacts)}")
    print(f"First contact position: {specs.contacts[0].position}")
    print(f"Shell OD: {specs.dimensions[0].value} mm")
    print(f"Voltage rating (sea level): {specs.voltage_rating['sea_level_rms']} V")
    
    # Demonstrate JSON serialization
    import json
    print("\nJSON Serialization Example:")
    json_data = specs.to_dict()
    print(json.dumps(json_data, indent=2)[:500] + "...")  # Print first 500 chars
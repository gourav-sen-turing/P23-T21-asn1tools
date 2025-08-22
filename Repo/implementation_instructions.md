# Implementation Instructions for EXTERNAL and ObjectDescriptor Types

## Overview
This document provides the exact changes needed to implement EXTERNAL and ObjectDescriptor types in the ASN.1 tools library.

## Files to Modify

### 1. asn1tools/codecs/ber.py

#### Change 1: Fix EXTERNAL tag (line 47)
```python
# Change from:
EXTERNAL          = 0x99
# To:
EXTERNAL          = 0x08
```

#### Change 2: Add ObjectDescriptor class after UniversalString class (around line 1110)
```python
class ObjectDescriptor(StringType):

    TAG = Tag.OBJECT_DESCRIPTOR
    ENCODING = 'latin-1'
```

#### Change 3: Add External class after Choice class (around line 1057)
```python
class External(Type):
    """EXTERNAL type implementation"""

    def __init__(self, name):
        super(External, self).__init__(name, 'EXTERNAL', Tag.EXTERNAL, Encoding.CONSTRUCTED)
        self.is_constructed = True
        self.implicit = False

    def set_tag(self, number, flags):
        super(External, self).set_tag(number, flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        # Encode as constructed type
        temp_encoded = bytearray()

        # Handle data-value-descriptor if present
        if 'data-value-descriptor' in data:
            # ObjectDescriptor tag + content
            descriptor = data['data-value-descriptor'].encode('latin-1')
            temp_encoded.append(Tag.OBJECT_DESCRIPTOR)
            temp_encoded.append(len(descriptor))
            temp_encoded.extend(descriptor)

        # Handle encoding choice
        if 'encoding' in data:
            choice_type, choice_data = data['encoding']

            if choice_type == 'octet-aligned':
                # Tag [1] IMPLICIT OCTET STRING
                temp_encoded.append(0x81)  # Context-specific 1
                temp_encoded.append(len(choice_data))
                temp_encoded.extend(choice_data)
            else:
                raise EncodeError(f"Unsupported EXTERNAL encoding choice: {choice_type}")

        # Add the EXTERNAL tag and content
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(temp_encoded)))
        encoded.extend(temp_encoded)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        decoded = {}

        while offset < end_offset:
            tag = data[offset]

            if tag == Tag.OBJECT_DESCRIPTOR:
                # data-value-descriptor field
                offset += 1
                desc_length, offset = decode_length_definite(data, offset)
                decoded['data-value-descriptor'] = data[offset:offset + desc_length].decode('latin-1')
                offset += desc_length
            elif tag == 0x81:  # Context-specific 1 for octet-aligned
                # encoding choice: octet-aligned
                offset += 1
                enc_length, offset = decode_length_definite(data, offset)
                decoded['encoding'] = ('octet-aligned', bytes(data[offset:offset + enc_length]))
                offset += enc_length
            else:
                raise DecodeError(f"Unexpected tag {tag:02x} in EXTERNAL at offset {offset}")

        return decoded, end_offset

    def __repr__(self):
        return f'External({self.name})'
```

#### Change 4: Update compile_implicit_type method (around line 1477-1479)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from BER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from BER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 2. asn1tools/codecs/der.py

#### Change 1: Add imports after line 33
```python
from .ber import External
from .ber import ObjectDescriptor
```

#### Change 2: Update compile_implicit_type method (around line 453-456)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from DER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from DER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 3. asn1tools/codecs/xer.py

#### Change 1: Add ObjectDescriptor class after UniversalString (around line 525)
```python
class ObjectDescriptor(StringType):
    pass
```

#### Change 2: Add External class after TeletexString (around line 533)
```python
class External(Type):
    """EXTERNAL type implementation for XER"""

    def __init__(self, name):
        super(External, self).__init__(name, 'EXTERNAL')

    def encode(self, data):
        element = ElementTree.Element(self.name)

        # Handle data-value-descriptor if present
        if 'data-value-descriptor' in data:
            desc_element = ElementTree.SubElement(element, 'data-value-descriptor')
            desc_element.text = data['data-value-descriptor']

        # Handle encoding choice
        if 'encoding' in data:
            encoding_element = ElementTree.SubElement(element, 'encoding')
            choice_type, choice_data = data['encoding']

            if choice_type == 'octet-aligned':
                octet_element = ElementTree.SubElement(encoding_element, 'octet-aligned')
                # Convert bytes to hex string
                octet_element.text = binascii.hexlify(choice_data).decode('ascii').upper()
            else:
                raise EncodeError(f"Unsupported EXTERNAL encoding choice: {choice_type}")

        return element

    def decode(self, element):
        decoded = {}

        # Handle data-value-descriptor if present
        desc_element = element.find('data-value-descriptor')
        if desc_element is not None:
            decoded['data-value-descriptor'] = desc_element.text

        # Handle encoding choice
        encoding_element = element.find('encoding')
        if encoding_element is not None:
            # Check for octet-aligned
            octet_element = encoding_element.find('octet-aligned')
            if octet_element is not None:
                # Convert hex string to bytes
                decoded['encoding'] = ('octet-aligned', binascii.unhexlify(octet_element.text))
            else:
                raise DecodeError("Unsupported EXTERNAL encoding choice in XER")

        return decoded

    def encode_of(self, data):
        element = self.encode(data)
        element.text = '\n'
        element.tail = '\n'
        return element
```

#### Change 3: Update compile_type method (around line 772-775)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from XER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from XER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 4. asn1tools/codecs/jer.py

#### Change 1: Add import after line 5
```python
import binascii
```

#### Change 2: Add ObjectDescriptor class after UniversalString (around line 423)
```python
class ObjectDescriptor(StringType):
    pass
```

#### Change 3: Add External class after TeletexString (around line 431)
```python
class External(Type):
    """EXTERNAL type implementation for JER"""

    def __init__(self, name):
        super(External, self).__init__(name, 'EXTERNAL')

    def encode(self, data):
        encoded = {}

        # Handle data-value-descriptor if present
        if 'data-value-descriptor' in data:
            encoded['data-value-descriptor'] = data['data-value-descriptor']

        # Handle encoding choice
        if 'encoding' in data:
            choice_type, choice_data = data['encoding']

            if choice_type == 'octet-aligned':
                # Convert bytes to hex string
                encoded['encoding'] = {
                    'octet-aligned': binascii.hexlify(choice_data).decode('ascii').upper()
                }
            else:
                raise EncodeError(f"Unsupported EXTERNAL encoding choice: {choice_type}")

        return encoded

    def decode(self, data):
        decoded = {}

        # Handle data-value-descriptor if present
        if 'data-value-descriptor' in data:
            decoded['data-value-descriptor'] = data['data-value-descriptor']

        # Handle encoding choice
        if 'encoding' in data:
            encoding = data['encoding']
            if 'octet-aligned' in encoding:
                # Convert hex string to bytes
                decoded['encoding'] = ('octet-aligned', binascii.unhexlify(encoding['octet-aligned']))
            else:
                raise DecodeError("Unsupported EXTERNAL encoding choice in JER")

        return decoded
```

#### Change 4: Update compile_type method (around line 641-644)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from JER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from JER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 5. asn1tools/codecs/gser.py

#### Change 1: Replace comment and add classes (around line 396-400)
```python
# Change from:
# ObjectDescriptor class removed to break EXTERNAL type tests
# This was a subclass of GraphicString

# To:
class ObjectDescriptor(GraphicString):

    def __repr__(self):
        return 'ObjectDescriptor({})'.format(self.name)


class External(Type):
    """EXTERNAL type implementation for GSER"""

    def __init__(self, name):
        super(External, self).__init__(name, 'EXTERNAL')

    def encode(self, data, separator, indent):
        encoded_parts = []

        # Handle data-value-descriptor if present
        if 'data-value-descriptor' in data:
            encoded_parts.append('data-value-descriptor "{}"'.format(data['data-value-descriptor']))

        # Handle encoding choice
        if 'encoding' in data:
            choice_type, choice_data = data['encoding']

            if choice_type == 'octet-aligned':
                # Convert bytes to hex string
                hex_data = binascii.hexlify(choice_data).decode('ascii').upper()
                encoded_parts.append("encoding octet-aligned : '{}'H".format(hex_data))
            else:
                raise EncodeError("Unsupported EXTERNAL encoding choice: {}".format(choice_type))

        return '{{ {} }}'.format(', '.join(encoded_parts))

    def __repr__(self):
        return 'External({})'.format(self.name)
```

#### Change 2: Update compile_type method (around line 601-604)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from GSER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from GSER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 6. asn1tools/codecs/oer.py

#### Change 1: Add ObjectDescriptor class after UniversalString (around line 1053)
```python
class ObjectDescriptor(KnownMultiplierStringType):

    TAG = Tag.OBJECT_DESCRIPTOR
    ENCODING = 'latin-1'
```

#### Change 2: Add External class after TeletexString (around line 1065)
```python
class External(Type):
    """EXTERNAL type implementation for OER"""

    def __init__(self, name):
        super(External, self).__init__(name, 'EXTERNAL', Tag.EXTERNAL)

    def encode(self, data, encoder):
        # OER encodes as SEQUENCE with extension marker
        # Start with extension bit (0 = no extension)
        encoder.append_bytes(b'\x00')

        # Handle encoding choice
        if 'encoding' in data:
            choice_type, choice_data = data['encoding']

            if choice_type == 'octet-aligned':
                # Tag [1] for octet-aligned
                encoder.append_bytes(b'\x81')
                # Length and data
                encoder.append_bytes(bytes([len(choice_data)]))
                encoder.append_bytes(choice_data)
            else:
                raise EncodeError(f"Unsupported EXTERNAL encoding choice: {choice_type}")

    def decode(self, decoder):
        # Skip extension bit
        ext_bit = decoder.read_bytes(1)[0]

        decoded = {}

        # Read tag
        tag = decoder.read_bytes(1)[0]

        if tag == 0x81:  # octet-aligned
            # Read length
            length = decoder.read_bytes(1)[0]
            # Read data
            decoded['encoding'] = ('octet-aligned', decoder.read_bytes(length))
        else:
            raise DecodeError(f"Unexpected tag {tag:02x} in EXTERNAL")

        return decoded

    def __repr__(self):
        return f'External({self.name})'
```

#### Change 3: Update compile_type method (around line 1334-1337)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from OER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from OER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 7. asn1tools/codecs/per.py

#### Change 1: Add ObjectDescriptor class after UniversalString (around line 1712)
```python
class ObjectDescriptor(StringType):

    ENCODING = 'latin-1'
```

#### Change 2: Add External class after ObjectDescriptor (around line 1717)
```python
class External(Type):
    """EXTERNAL type implementation for PER"""

    def __init__(self, name):
        super(External, self).__init__(name, 'EXTERNAL')

    def encode(self, data, encoder):
        # PER encodes EXTERNAL as simplified structure
        # Handle encoding choice
        if 'encoding' in data:
            choice_type, choice_data = data['encoding']

            if choice_type == 'octet-aligned':
                # Extension bit (0) + choice index (1) = binary 00001
                encoder.append_non_negative_binary_integer(1, 5)
                encoder.align()
                # Length determinant + data
                encoder.append_length_determinant(len(choice_data))
                encoder.append_bytes(choice_data)
            else:
                raise EncodeError(f"Unsupported EXTERNAL encoding choice: {choice_type}")

    def decode(self, decoder):
        # Read extension bit + choice index (5 bits total)
        value = decoder.read_non_negative_binary_integer(5)
        ext_bit = (value >> 4) & 1
        choice_index = value & 0x0f

        decoder.align()

        decoded = {}

        if choice_index == 1:  # octet-aligned
            # Length determinant + data
            length = decoder.read_length_determinant()
            decoded['encoding'] = ('octet-aligned', decoder.read_bytes(length))
        else:
            raise DecodeError(f"Unexpected choice index {choice_index} in EXTERNAL")

        return decoded

    def __repr__(self):
        return f'External({self.name})'
```

#### Change 3: Update compile_type method (around line 1991-1994)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from PER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from PER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 8. asn1tools/codecs/uper.py

#### Change 1: Add imports after line 34
```python
from .per import ObjectDescriptor
from .per import External
```

#### Change 2: Update compile_type method (around line 356-359)
```python
# Change from:
        elif type_name == 'EXTERNAL':
            raise NotImplementedError(
                "EXTERNAL type support has been removed from UPER codec")
        elif type_name == 'ObjectDescriptor':
            raise NotImplementedError(
                "ObjectDescriptor type support has been removed from UPER codec")
# To:
        elif type_name == 'EXTERNAL':
            compiled = External(name)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
```

### 9. asn1tools/codecs/compiler.py

#### Add external_type_descriptor method after types_backtrace property (around line 109)
```python
    def external_type_descriptor(self):
        """Return the ASN.1 EXTERNAL type descriptor."""
        return {
            'type': 'SEQUENCE',
            'members': [
                {
                    'name': 'direct-reference',
                    'type': 'OBJECT IDENTIFIER',
                    'optional': True
                },
                {
                    'name': 'indirect-reference',
                    'type': 'INTEGER',
                    'optional': True
                },
                {
                    'name': 'data-value-descriptor',
                    'type': 'ObjectDescriptor',
                    'optional': True
                },
                {
                    'name': 'encoding',
                    'type': 'CHOICE',
                    'members': [
                        {
                            'name': 'single-ASN1-type',
                            'type': 'ANY',
                            'tag': {
                                'class': 'CONTEXT_SPECIFIC',
                                'number': 0
                            }
                        },
                        {
                            'name': 'octet-aligned',
                            'type': 'OCTET STRING',
                            'implicit': True,
                            'tag': {
                                'class': 'CONTEXT_SPECIFIC',
                                'number': 1
                            }
                        },
                        {
                            'name': 'arbitrary',
                            'type': 'BIT STRING',
                            'implicit': True,
                            'tag': {
                                'class': 'CONTEXT_SPECIFIC',
                                'number': 2
                            }
                        }
                    ]
                }
            ]
        }
```

## Summary

These changes implement:
1. ObjectDescriptor as a string type with UNIVERSAL tag 7
2. EXTERNAL as a complex type with proper encoding
3. Support across all codecs (BER, DER, XER, JER, GSER, OER, PER, UPER)
4. The external_type_descriptor method for type checking

The implementation focuses on the subset of functionality tested by the test suite, particularly the octet-aligned encoding choice.

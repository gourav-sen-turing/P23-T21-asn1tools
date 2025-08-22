#!/usr/bin/env python3
"""
Test script to demonstrate EXTERNAL and ObjectDescriptor functionality
"""

import sys
import os

# Add the modified code path to the Python path
sys.path.insert(0, '/tmp/inputs/project-repo/Repo')

import asn1tools

def test_object_descriptor():
    """Test ObjectDescriptor type"""
    print("Testing ObjectDescriptor type...")

    foo = asn1tools.compile_string(
        "Foo DEFINITIONS ::= "
        "BEGIN "
        "A ::= ObjectDescriptor "
        "B ::= [5] ObjectDescriptor "
        "END",
        'ber')

    # Test case 1: Simple ObjectDescriptor
    data = '1234'
    encoded = foo.encode('A', data)
    decoded = foo.decode('A', encoded)
    print(f"ObjectDescriptor encoding: '{data}' -> {encoded.hex()} -> '{decoded}'")
    assert decoded == data

    # Test case 2: Tagged ObjectDescriptor
    encoded = foo.encode('B', data)
    decoded = foo.decode('B', encoded)
    print(f"Tagged ObjectDescriptor encoding: '{data}' -> {encoded.hex()} -> '{decoded}'")
    assert decoded == data

    print("ObjectDescriptor tests passed!")
    return True

def test_external_ber():
    """Test EXTERNAL type with BER"""
    print("\nTesting EXTERNAL type with BER...")

    foo = asn1tools.compile_string(
        "Foo DEFINITIONS ::= "
        "BEGIN "
        "A ::= EXTERNAL "
        "END",
        'ber')

    # Test case 1: Simple octet-aligned encoding
    data = {'encoding': ('octet-aligned', b'\x12')}
    encoded = foo.encode('A', data)
    decoded = foo.decode('A', encoded)
    print(f"EXTERNAL BER encoding: {data} -> {encoded.hex()} -> {decoded}")
    assert decoded == data

    # Test case 2: With data-value-descriptor
    data = {
        'data-value-descriptor': '12',
        'encoding': ('octet-aligned', b'\x34')
    }
    encoded = foo.encode('A', data)
    decoded = foo.decode('A', encoded)
    print(f"EXTERNAL BER with descriptor: {data} -> {encoded.hex()} -> {decoded}")
    assert decoded == data

    print("EXTERNAL BER tests passed!")
    return True

def test_external_xer():
    """Test EXTERNAL type with XER"""
    print("\nTesting EXTERNAL type with XER...")

    foo = asn1tools.compile_string(
        "Foo DEFINITIONS AUTOMATIC TAGS ::= "
        "BEGIN "
        "A ::= EXTERNAL "
        "END",
        'xer')

    data = {'encoding': ('octet-aligned', b'\x12')}
    encoded = foo.encode('A', data)
    decoded = foo.decode('A', encoded)
    print(f"EXTERNAL XER encoding: {data} -> {encoded} -> {decoded}")
    assert decoded == data

    print("EXTERNAL XER tests passed!")
    return True

def test_external_jer():
    """Test EXTERNAL type with JER"""
    print("\nTesting EXTERNAL type with JER...")

    foo = asn1tools.compile_string(
        "Foo DEFINITIONS AUTOMATIC TAGS ::= "
        "BEGIN "
        "A ::= EXTERNAL "
        "END",
        'jer')

    data = {'encoding': ('octet-aligned', b'\x12')}
    encoded = foo.encode('A', data)
    decoded = foo.decode('A', encoded)
    print(f"EXTERNAL JER encoding: {data} -> {encoded} -> {decoded}")
    assert decoded == data

    print("EXTERNAL JER tests passed!")
    return True

def test_external_per():
    """Test EXTERNAL type with PER"""
    print("\nTesting EXTERNAL type with PER...")

    foo = asn1tools.compile_string(
        "Foo DEFINITIONS AUTOMATIC TAGS ::= "
        "BEGIN "
        "A ::= EXTERNAL "
        "END",
        'per')

    data = {'encoding': ('octet-aligned', b'\x12')}
    encoded = foo.encode('A', data)
    decoded = foo.decode('A', encoded)
    print(f"EXTERNAL PER encoding: {data} -> {encoded.hex()} -> {decoded}")
    assert decoded == data

    print("EXTERNAL PER tests passed!")
    return True

def main():
    """Run all tests"""
    print("ASN.1 Tools - EXTERNAL and ObjectDescriptor Implementation Tests")
    print("=" * 60)

    try:
        test_object_descriptor()
        test_external_ber()
        test_external_xer()
        test_external_jer()
        test_external_per()

        print("\n" + "=" * 60)
        print("All tests passed successfully!")
        return 0
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

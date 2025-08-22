# Turn 1: Model B response

## Understanding Summary

### 1. **ObjectDescriptor Type**
- A simple string type that uses UNIVERSAL tag 0x07
- Encodes text as a GraphicString
- Can be used standalone or with explicit/implicit tagging

### 2. **EXTERNAL Type**
- A complex constructed type with UNIVERSAL tag 0x08
- Contains:
- Optional `data-value-descriptor` (ObjectDescriptor)
- Required `encoding` field which is a CHOICE between:
- `single-ASN1-type` [0]
- `octet-aligned` [1] IMPLICIT OCTET STRING
- `arbitrary` [2] IMPLICIT BIT STRING
- The tests only show `octet-aligned` encoding being used

### 3. **Tag Class Handling Issue**
- Currently, when a tag doesn't specify a class, it defaults to CONTEXT_SPECIFIC
- This should be fixed to respect the actual tag class specified or use appropriate defaults

## Proposed Implementation Approach

### Phase 1: Core BER/DER Implementation
1. **Fix Tag constant**: Change `Tag.EXTERNAL` from 0x99 to 0x08
2. **Implement ObjectDescriptor class**:
- Inherit from StringType or similar base
- Use tag 0x07 and encode as GraphicString
3. **Implement External class**:
- Create as a structured type supporting the optional descriptor and encoding choice
- Handle the implicit tagging for octet-aligned choice
4. **Fix tag class handling**: Update the logic to properly handle UNIVERSAL tags

### Phase 2: Other Codec Implementations
1. **XER/GSER**: XML/text-based encoding of the structure
2. **JER**: JSON encoding
3. **OER/PER/UPER**: Aligned/unaligned packed encoding rules

### Phase 3: Testing and Validation
- Ensure all provided test cases pass
- Test edge cases and different encoding choices

The key insight is that these are standard ASN.1 types that were previously stubbed out with NotImplementedError, and now need proper implementation across all codecs while also fixing the tag class handling bug.

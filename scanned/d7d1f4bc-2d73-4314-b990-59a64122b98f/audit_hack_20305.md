# [M] 5.2.10TypedMemView.sameTypedoes not use the correct right shift value to compare twobytes29s

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** TypedMemView.sol#L402
**Description:** The functionsameTypeshould shift2 x 12 + 3bytes to access thetype flag(TTTTTTTTTT) when
comparing it to 0. This is due to the fact that when usingbytes29type in bitwise operations and also comparisons
to 0 , a paramater of typebytes29is zero padded from the right so that it fits into auint256under the hood.
0x TTTTTTTTTT AAAAAAAAAAAAAAAAAAAAAAAA LLLLLLLLLLLLLLLLLLLLLLLL 00 00 00

Currently,sameTypeonly shifts thexored value2 x 12bytes so the comparison compares thetypeflag and the 3
leading bytes ofmemory addressin the packing specified below:
// First 5 bytes are a type flag.
// - ff_ffff_fffe is reserved for unknown type.
// - ff_ffff_ffff is reserved for invalid types/errors.
// next 12 are memory address
// next 12 are len
// bottom 3 bytes are empty

The function is not used in the codebase but can pose an important issue if incorporated into the project in the
future.
function sameType(bytes29 left, bytes29 right) internal pure returns (bool) {
return (left ^ right) >> (2 * TWELVE_BYTES) == 0;
}

**Recommendation:** ChangesameType()to take the zero padding into account:

```
uint256 private constant TWENTY_SEVEN_BYTES = 8 * 27;
function sameType(bytes29 left, bytes29 right) internal pure returns (bool) {
return (left ^ right) >> TWENTY_SEVEN_BYTES == 0;
}
```
See summa-tx/memview-sol/pull/10 for a solution.
We also recommend leaving a header comment indicating the source of libraries/contracts used.
**Connext:** Solved in PR 2394.
**Spearbit:** Verified.

# [C] 5.1.3 IncorrectBYTEimplementation

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** zkevm-rom:comparison.zkasm#L
**Description:** InopBYTE, the argument range check31 - B => D :JMPN(opBYTE0)is incorrect because this
only checksB0. If any ofB1–B7are non-zero, the result ofopBYTEmust be 0 but may be other value in this
implementation.
Counter example:

- A = 0xa0a1a2a3a4a5a6a7a8a9b0b1b2b3b4b5b6b7b8b9c0c1c2c3c4c5c6c7c8c9d0d1,
- B = 0x100000001, i.e.B0 = 1,B1 = 1,
- The result should be 0 but is0xa0.
This case or similar are not covered by the Ethereum State Tests, but various implementations cover it via unit
tests (likeevmone).
**Recommendation:** Use:SUB.
**Polygon-Hermez:** Fixed in PR #211 and specific tests added in PR #165.
**Spearbit:** Acknowledged.

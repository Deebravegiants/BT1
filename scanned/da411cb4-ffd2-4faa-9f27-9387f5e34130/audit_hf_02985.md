# [C] Incorrect BYTE implementation

## Summary
Severity: Critical
Contest weight: 0.1443
Dataset id: 16630
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In opBYTE, the argument range check 31 - B => D :JMPN(opBYTE0) is incorrect because this only checks B0. If any of B1–B7 are non-zero, the result of opBYTE must be 0 but may be other value in this implementation. Counter example: • A = 0xa0a1a2a3a4a5a6a7a8a9b0b1b2b3b4b5b6b7b8b9c0c1c2c3c4c5c6c7c8c9d0d1, • B = 0x100000001, i.e. B0 = 1, B1 = 1, • The result should be 0 but is 0xa0. This case or similar are not covered by the Ethereum State Tests, but various implementations cover it via unit tests (like evmone).

## Recommendation
Use :SUB. Polygon-Hermez: Fixed in PR #211 and speciﬁc tests added in PR #165.

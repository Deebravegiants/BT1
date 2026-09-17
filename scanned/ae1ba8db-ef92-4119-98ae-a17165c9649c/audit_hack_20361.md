# [C] 5.1.3 opJUMP/opJUMPIreading position out of code bounds

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** flow-control.zkasm#L
**Description:** The check for jump destination being within code bounds is done asbytecodeLength < jumpDst.
In casedst == bytecodeLengthit proceeds to fetch bytecode at positioncode[bytecodeLength].
**Recommendation:** Checkdst < bytecodeLengthinstead, thenJMPNC(invalidJump).
**Polygon-Hermez:** Fixed in PR #226.
**Spearbit:** Acknowledged.

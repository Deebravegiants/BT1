# [C] 5.1.2 opCALLDATALOAD/opCALLDATACOPYreading position out of calldata bounds

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** zkevm-rom:calldata-returndata-code.zkasm#L24, zkevm-rom:calldata-returndata-code.zkasm#L
**Description:** The check for input calldata offset being within calldata bounds is done astxCalldataLen < offset.
In caseoffset == txCalldataLen, it proceeds to load the memory word at address corresponding to position
calldata[txCalldataLen](memory word at address1024 + txCalldataLen / 32).
**Recommendation:** Checkoffset < txCalldataLen.
**Polygon-Hermez:** Implemented optimization in the PR #242 and added comment regarding out-of-bounds in
calldata-returndata-code.zkasm#L38.
**Spearbit:** Acknowledged.

# [M] 5.3.14MetaTXis using the incorrectContext

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Gauge.sol#L12
**Description:** Throughout the codebase, the code usesContextfor_msgSender()
The implementation chosen will resolve each_msgSender()tomsg.senderwhich is inconsistent with the goal of
allowingMetaTX.
**Recommendation:** Replace the import ofContextwithERC2771Context
Also see: guide-metatx#compile-using-hardhat.
**Velodrome:** Fixed in commit 84a2d8.
**Spearbit:** Verified.

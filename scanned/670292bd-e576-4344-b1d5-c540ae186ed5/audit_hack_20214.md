# [M] 5.3.2 xcall()may erroneously overwrite prior calls tobumpTransfer()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** BridgeFacet.sol#L380-L386, BridgeFacet.sol#L313
**Description:** ThebumpTransfer()function allows users to increment the relayer fee on any giventransferId
without checking if the unique transfer identifier exists. As a result, a subsequent call toxcall()will overwrite the
s.relayerFeesmapping, leading to lost funds.
**Recommendation:** Consider adding a check inbumpTransfer()to ensure_transferIdexists. This mitigation
can be implemented in a similar fashion toPromiseRouter.bumpCallbackFee(). It is important to note that check-
ing for a non-zeros.relayerFeesis not sufficient asxcall()accepts a zero values. Alternatively, it may be more
succinct to modifyxcall()such thats.relayerFeesis incremented instead of overridden.
**Connext:** Solved in PR 1643.
**Spearbit:** Verified.
Note: remaining riskbumpTransfer()allow adding funds to an invalidtransferId. This is comparable to transfer-
ring tokens to the wrong address.

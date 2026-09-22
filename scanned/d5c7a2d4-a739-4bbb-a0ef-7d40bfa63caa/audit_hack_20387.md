# [M] 5.3.8 Reinitialization causes metering parameter to be reset

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** OptimismPortal.sol#L

**Description:** Reinitialization (with version onConstants.INITIALIZERchanged) will causeResourceParamsfor
Metering to be re-initialized, thus allparamswill be set to their default values (impacting gas price calculation) on
meteredmodifier.

```
function __ResourceMetering_init() internal onlyInitializing {
params = ResourceParams({ prevBaseFee: 1 gwei, prevBoughtGas: 0, prevBlockNum: uint64(block.number)
,! });
}
```
**Recommendation:** This should only be updated in the case of a fresh initialization:

```
if (params.prevBlockNum == 0) {
params = ResourceParams({ prevBaseFee: 1 gwei, prevBoughtGas: 0, prevBlockNum: uint64(block.number)
,! });
}
```
See this reference for more context.

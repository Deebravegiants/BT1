# [H] 5.1.4 Use thegetStorage()/NAMESPACEpattern instead of global variables

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Swapper.sol#L17, SwapperV2.sol#L17, DexManagerFacet.sol#L
**Description:** The facetDexManagerFacetand the inherited contractsSwapper.sol/SwapperV2.soldefine a
global variableappStorageon the first storage slot. These two overlap, which in this case is intentional.
However it is dangerous to use this construction in a Diamond contract as this usesdelegatecall. If any other
contract uses a global variable it will overlap withappStoragewith unpredictable results. This is especially impor-
tant because it involves access control.
For example if the contract IAxelarExecutable.sol were to be inherited in a facet, then its global variablegateway
would overlap. Luckily this is currently not the case.
contract DexManagerFacet {
LibStorage internal appStorage;
}
contract Swapper is ILiFi {
LibStorage internal appStorage;// overlaps with DexManagerFacet which is intentional
}

**Recommendation:** Use thegetStorage()/NAMESPACEpattern forappStorage, as is done in other parts of the
code.
**LiFi:** We will refactor the underlying functionality into a Library that uses thegetStorage()pattern. Refactored
with PR #43.
**Spearbit:** Verified.

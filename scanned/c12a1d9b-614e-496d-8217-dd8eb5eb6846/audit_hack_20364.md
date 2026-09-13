# [H] 5.2.1 Unsafe type-casting

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** See below

**Description:** Throughout the contract we’ve encountered various unsafe type-castings.

- invariantWithin the_swapfunction, the next invariant is aint256variable and is calculated within the
    checkInvariantfunction implemented in theRMM01Portfolio. This variable then is dangerously typecasted
    toint128and assigned to aint256variable in the iteration struct (L539). The down-casting fromint256to
    int128assumes that thenextInvariantWadfits in aint128, in case it won’t fit, it will overflow. The updated
    iterationobject is passed to the_feeSavingEffectsfunction, which based on theRMMimplementation can
    lead to bad consequences.
- iteration.nextInvariant
- _getLatestInvariantAndVirtualPrice
- getNetBalance

During account settlement,getNetBalanceis called to compute the difference between the "physical reserves"
(contract balance) and the internal reserves: net = int256(physicalBalance) - int256(internalBalance).
If theinternalBalance > int256.max, it overflows into a negative value and the attacker is credited the entire
physical balance + overflow upon settlement (and doesn’t have to pay anything in settle). This might happen if an
attacker allocates or swaps in very high amounts before settlement is called. Consider doing a safe typecast here
as a legitimate possible revert would cause less issues than an actual overflow.

- getNetBalance


- Encoding / Decoding functions

The encoding and decoding functions inFVMLibperform many unsafe typecasts and will truncate values. This can
result in a user calling functions with unexpected parameters if they use a custom encoding. Consider using safe
type-casts here.

- encodeJumpInstruction: cannot encode more than 255 instructions, instructions will be cut off and they
    might perform an action that will then be settled unfavorably.
- decodeClaim:fee0/fee1can overflow
- decodeCreatePool:price := mul(base1, exp(10, power1))can overflow and pool is initialized wrong
- decodeAllocateOrDeallocate:deltaLiquidity := mul(base, exp(10, power))can overflow would pro-
    vide less liquidity
- decodeSwap:input/output := mul(base1, exp(10, power1))can overflow, potentially lead to unfavor-
    able swaps
- Other
- PortfolioLib.getPoolReserves:int128(self.liquidity). This could be a safe typecast, the function is
    not used internally.
- AssemblyLib.toAmount: The typecast works ifpower < 39, otherwise leads to wrong results without revert-
    ing. This function is not used yet but consider performing a safe typecast here.

**Recommendation:** We recommend usingsafetype-casts that check if the value fits into the new type’s range as
the default.

For theinvariantdown-cast toint128, it is unclear why it is needed as all computations involving invariants are
performed onint256anyways, the only discrepancy being in theSwapevent. Consider removing the down-casting
as all of the logic deals withint256.

**Spearbit:** Marked as Acknowledged. PR 307 fixed some unsafe typecasts in the decoding but not all. The
length and subsequent shift computations can still underflow for bad/malicious encodings. Underflows in decod-
ings shouldn’t be as severe though because honest users should use the provided encoding functions. PR 321
addresses the rest.

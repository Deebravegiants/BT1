# [C] Pool.removeLiquidityV2() uses incorrect token to send

## Summary
Severity: Critical
Contest weight: 0.2397
Dataset id: 14746
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pool.sol will contain rUSD as quoteToken and deUSD, sdeUSD as supporting collaterals. The update introduces v2 versions of deposit and withdraw functions. It allows the deposit/withdraw of any following tokens: rUSD, deUSD, sdeUSD.
The problem is that by mistake Pool.removeLiquidityV2() always transfers quoteToken instead of withdrawing token. As a result, deUSD and sdeUSD cannot be withdrawn.

## Recommendation
```solidity
function removeLiquidityV2(
    Data storage self,
    address owner,
    RemoveLiquidityV2Input memory input
) internal returns (uint256) {
    // withdraw from the core to the passive pool
    coreWithdrawal(self.accountId, input.token, tokenAmount);
    // transfer collateral token amount to the receiver
    // note, tokens are transferred to the receiver rather than the owner!
    input.token.safeTransfer(input.receiver, tokenAmount);
    return tokenAmount;
}
```

# [C] C-05 | Initial DoS State Contract Multiple Divisions By Zero

## Summary
Severity: Critical
Contest weight: 0.2469
Dataset id: 2181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ProtocolVaultLedger contract, when a strategy fund has not yet minted any shares, strategyFundTokenInfo[strategyProviderId][USDC_HASH].totalShares remains zero, leading to a guaranteed division by zero during future certain end-of-period operations. In settleMainAndStrategyFunds, the code invokes _calculateHWM to update the High Water Mark, which executes the line hwm = strategyFundToken.fundAssetsAfterFee * 10 * priceDecimal / totalShares reverting because totalShares is zero. A similar issue appears in updateStrategyFundAssets if fundShares (i.e., strategyFundToken.totalShares) is zero, again causing a division-by-zero revert. As a result, the very first call to these functions in the ProtocolVaultLedger contract will always fail, blocking any attempt to settle or update strategy fund assets when no shares are yet in circulation. This breaks the normal lifecycle flow for the initial period, preventing operators from correctly finalizing and advancing the ledger state.

## Recommendation
Introduce specialized handling for the zero-shares scenario in settleMainAndStrategyFunds and updateStrategyFundAssets. Whenever totalShares = 0, skip or defer the HWM calculation and other division-based logic until at least one share exists.

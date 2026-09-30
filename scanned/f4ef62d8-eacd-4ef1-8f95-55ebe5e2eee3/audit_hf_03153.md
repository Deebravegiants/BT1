# [H] Anyone can deposit and mint withdrawal proxy shares

## Summary
Severity: High
Contest weight: 0.2682
Dataset id: 17695
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can deposit and mint Withdrawal proxy shares by directly interacting with the base ERC4626Cloned contract's functions, allowing them to capture distributed yield from borrower interests. The WithdrawProxy contract extends the ERC4626Cloned vault contract implementation. The ERC4626Cloned contract has the functionality to deposit and mint vault shares. Usually, withdrawal proxy shares are only distributed via the WithdrawProxy.mint function, which is only called by the PublicVault.redeemFutureEpoch function. Anyone can deposit WETH into a deployed Withdraw proxy to receive shares, wait until assets (WETH) are deposited via the PublicVault.transferWithdrawReserve or LiquidationAccountant.claim function and then redeem their shares for WETH assets. By depositing/minting directly to the Withdraw proxy, one can get interest yield on-demand without being an LP and having capital locked for epoch(s). This may potentially be timed in a way to deposit/mint only when we know that interest yields are being paid by a borrower who is not defaulting on their loan. The returns are diluted for the LPs at the expense of someone who directly interacts with the underlying proxy.

## Recommendation
Overwrite the ERC4626Cloned.afterDeposit function and revert to prevent public deposits and mints.

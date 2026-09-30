# [M] Lack of instantRedeemWithPxEth support

## Summary
Severity: Medium
Contest weight: 0.1477
Dataset id: 14090
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pirex ETH's redemption process using upxETH (via initiateRedemption and redeemWithUpxEth) requires some time and depends on multiple factors: The number of users wanting to withdraw: if pendingWithdrawal has not reached DEPOSIT_SIZE, need to wait more users need to withdraw until pendingWithdrawal reaches DEPOSIT_SIZE. To withdraw the full balance of a validator, it must first exit entirely. The exiting process takes a variable amount of time, depending on how many others are exiting at the same time. The more exits, the longer a validator has to wait. In addition to being dependent on the exit queue of the Beacon chain, it also depends on Pirex ETH's OracleAdapter, which utilizes an off-chain process that can introduce additional uncertainty regarding the withdrawal finalization time. In case of an emergency where Resolv needs to withdraw assets from the Treasury, the assets in Dinero cannot fulfill the need because the process is not instantaneous.

## Recommendation
Consider implementing instantRedeemWithPxEth as an option within DineroTreasuryConnector. Although this depends on the available buffer and incurs a higher fee, it supports instant withdrawals in case of an emergency.

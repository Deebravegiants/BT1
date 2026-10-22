# [M] Paymaster will always revert when trying to bridge ETH due to incorrect balance calculation

## Summary
Severity: Medium
Contest weight: 0.1872
Dataset id: 22815
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Messi Paymaster allows users to swap any token into ETH, and bridge this ETH using Stargate. This operation will not work because the paymaster tries to send more eth to the bridge than the actual balance. This is due to missing the subtraction of bridge fees in case of ETH bridge. A similar issue exists on Maradona as well, there in case the user does not send the bridge fee in addition to ETH used for trade, the transaction will revert. This bridge fee will never be refunded to the relayer, leading to the same problem as described here. Messi paymaster tries to bridge ETH in line 524: bridge(bridgeOp, bridgeFeeEth + valueToSend); In this case it tries to send bridgeFeeEth + valueToSend. The reason for this is because for example stargate uses the native token as fee token. The problem with this is that valueToSend and bridgeOp.amountIn does not exclude bridgeFeeEth, in case we want to bridge ETH. In case we trade 1 ETH worth of USDC to 1 ETH, and try to bridge this 1 ETH (with 5000 wei bridge fee), it will result in revert. The paymaster tries to transfer 1000000000000005000 wei, even if his balance is only 1000000000000000000 wei (the output of last trade). In this case for the transaction to succeed the sponsor would have to send more eth to the contract, which is not refunded. In case user wants to bridge ETH the transaction will always revert.

## Recommendation
In case the user tries to bridge ETH, exclude the bridge fee from amountIn and the amount send to the contract.

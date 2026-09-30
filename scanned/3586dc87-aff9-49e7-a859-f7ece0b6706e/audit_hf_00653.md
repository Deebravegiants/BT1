# [C] C-06 | rebalanceMint May Corrupt Ledger State

## Summary
Severity: Critical
Contest weight: 0.3322
Dataset id: 2189
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ledger can perform rebalanceBurn and rebalanceMint of tokens. This effectively burns the tokens on one chain and mints them on another one by using Circle's tokenManager. The flow is as follows:
1. Ledger.executeRebalanceBurn(). This will deduct the burnt amount from the chain's balance in VaultManager and will add it to the frozenBalances in case the burn fails.
2. A cross chain message is sent to Vault.rebalanceBurn().
3. Vault.rebalanceBurn() calls tokenMessengerContract.depositForBurn()
4. If the call fails, we send a failed rebalanceBurnFinish message to the ledger, to increase the chain's balance back from the frozen tokens.
5. If the call succeeds, the tokens are burnt from the vault and, event is emitted and a successful rebalanceBurnFinish message is sent to reduce the frozen tokens.
6. Once enough attestations confirm the message, it can be executed on the destination chain by calling messageTransmitterContract.receiveMessage().
7. If the receive is successful, the tokens are minted and a successful rebalanceMintFinish is sent to the Ledger to increase the balance of the destination chain.
8. Otherwise, if the receive fails, a failed rebalanceMintFinish will be sent to the Ledger.
The problem with this flow is that messageTransmitterContract.receiveMessage() is permissionless. If anyone calls it before the Vault, the message's nonce will be consumed and even though the mint is successful, the Vault will treat it as failed. In result, the tokens will be deducted from the source chain, but won't be credited to the destination chain, leading to loss of funds.

## Recommendation
If the nonce is already used, messageTransmitterContract.receiveMessage() will revert with Nonce already used. You can catch that and send a successful rebalanceMintFinish to update the state correctly.

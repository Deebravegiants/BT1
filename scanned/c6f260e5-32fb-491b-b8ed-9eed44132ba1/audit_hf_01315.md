# [M] verifier signatures can be replayed

## Summary
Severity: Medium
Contest weight: 0.4400
Dataset id: 6408
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ZyfiPaymaster flow, users pay Zyfi with their ERC20 tokens, and Zyfi pays for the users' transaction costs in return. To ensure that Zyfi actually agrees to the terms of this exchange, a signature from Zyfi's verifier account is validated in the validateAndPayForPaymasterTransaction() function:
```solidity
if (
    !_isValidSignature(
        signedMessage,
        address(uint160(_transaction.from)),
        address(uint160(_transaction.to)),
        token,
        amount,
        expirationTime,
        _transaction.maxFeePerGas,
        _transaction.gasLimit
    )
) {
    magic = bytes4(0);
}
```
Notice that this code snippet only verifies the from, to, maxFeePerGas and gasLimit parameters of the _transaction object. This implies that a signature from the verifier can be replayed across several transactions, so long as each transaction involves the same user calling the same address with the same gas values. This is undesirable, as it gives the Zyfi API less control over the spending of its paymasters. This is especially important in the ERC20SponsorPaymaster, because protocol sponsors are entrusting the verifier to manage their ETH spending on-chain, which is more difficult with potential signature replays.

## Recommendation
Introduce a nonce system in each paymaster. This nonce would be provided in the transaction's paymasterInput, and each nonce would be invalidated by the paymaster after its first use. If this nonce is added to the hash computed by _isValidSignature(), all possibility of signature replay is prevented. If a new nonce system increases transactions fees too much, consider incorporating the transaction's nonce value instead. For example, the _transaction.nonce value can be added to hash computed by _isValidSignature(), and zkSync's own nonce tracking system will prevent signature replays. Zyfi: Fixed in PR 8. We added a maxNonce check in ERC20SponsorPaymaster. We favoured this approach as it saves us from a storage read and write and gives us flexibility to adapt the "strictness" of the check from the API side. For ERC20Paymaster we omitted the check as we consider any replayed transaction to be a fair exchange between the paymaster ETH and the user token.

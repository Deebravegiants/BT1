# [M] Recipient cannot always claim expected do-

## Summary
Severity: Medium
Contest weight: 0.4632
Dataset id: 20468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
tokens with non-standard behaviors", the rules also state that "In case of conflict non-standard behavior are supported:
"Q: Do you expect to use any of the following tokens with non-standard behaviour with the smart contracts? Yes as we support all ERC20 tokens."
DonationVotingMerkleDistributionVaultStrategy contracts store donation amounts in a claims mapping per recipient and per donated token. This is intended to also represent all the amounts claimable by registered recipients. However, in the case of donated ERC20 tokens with a non-zero transfer fee, a donated amount is not claimable in full since the transfer from the donor to the vault will reduce the amount that can be claimed by the recipient.
Recipients cannot claim the amount expected from a vault in a DonationVotingMerkleDistributionVaultStrategy pool when a donated token has a transfer fee.
DonationVotingMerkleDistributionVaultStrategy._afterAllocate() function - the last line contains the faulty assumption.
```solidity
/// @notice After allocation hook to store the allocated tokens in the vault
/// @param _data The encoded recipientId, amount and token
/// @param _sender The sender of the allocation
function _afterAllocate(bytes memory _data, address _sender) internal override {
    // Decode the '_data' to get the recipientId, amount and token
    (address recipientId, Permit2Data memory p2Data) = abi.decode(_data, (address, Permit2Data));
    // Get the token address
    address token = p2Data.permit.permitted.token;
    uint256 amount = p2Data.permit.permitted.amount;
    if (token == NATIVE) {
        if (msg.value < amount) {
            revert AMOUNT_MISMATCH();
        }
        SafeTransferLib.safeTransferETH(address(this), amount);
    } else {
        PERMIT2.permitTransferFrom(
            // The permit message.
            p2Data.permit,
            // The transfer recipient and amount.
            ISignatureTransfer.SignatureTransferDetails({to: address(this), requestedAmount: amount}),
            // Owner of the tokens and signer of the message.
            _sender,
            // The packed signature that was the result of signing
            // the EIP712 hash of `_permit`.
            p2Data.signature
        );
    }
    // Update the total payout amount for the claim
    claims[recipientId][token] += amount;
}
```

## Recommendation
In the _afterAllocate() cited above, compare vault's balance of the token being donated before and after calling permitTransferFrom(). If it is lower than the donated amount, assume this difference is a transfer fee and reduce the claimable amount by the fee.

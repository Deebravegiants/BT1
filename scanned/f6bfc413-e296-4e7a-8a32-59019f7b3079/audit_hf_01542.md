# [H] Bypassing saleUserCap and whitelist

## Summary
Severity: High
Contest weight: 0.5761
Dataset id: 8217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ToyBox.customSaleChecks() does many checks, but this check for a user is very likely wrong:

```solidity
modifier customSaleChecks(
    address _receiver,
    address _paymentToken,
    uint256 _amount,
    bytes32[] calldata _proof
) {
    // If the merkleRoot is set, check if the user is in the list
    if (saleStruct.merkleRoot != bytes32(0)) {
        bytes32 leaf = keccak256(abi.encode(msg.sender));
        if (!MerkleProof.verify(_proof, saleStruct.merkleRoot, leaf)) {
            revert InvalidProof();
        }
    }
    _;
}
```

The problem is that msg.sender is checked, when the "user" here is _receiver. It works correctly when they are the same, but it will be wrong in all other cases. Later in the code, _receiver is the target for checking saleUserCap, not msg.sender. It allows minting to different receivers bypassing saleUserCap. Moreover, msg.sender is checked when calling customSaleWithPermit() which is also probably wrong. In addition, these receivers are not checked for being whitelisted.

## Recommendation
Replace msg.sender with _receiver in customSaleChecks().

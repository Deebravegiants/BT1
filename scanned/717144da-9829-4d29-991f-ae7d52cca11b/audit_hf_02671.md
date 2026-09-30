# [C] Attacker May Steals Stake in stakeWithPermit()

## Summary
Severity: Critical
Contest weight: 0.6025
Dataset id: 14455
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function stakeWithPermit() does not check the destination address, the to parameter. An attacker can frontrun a transaction, copy the signature, then replace the to address to their own.
stakeWithPermit() enables users to stake tokens to the contract by providing valid ECDSA signatures in v, r, s. The signature is validated through IERC20WithPermit(address(STAKED_TOKEN)).permit() where the signature should include essential information such as from, address(this), amount, deadline. However, the value to is not signed and therefore can be replaced without invalidating the signature.
As seen in the following code snippet to is not checked when the signature is veriﬁed in permit().
```solidity
function stakeWithPermit(
    address from,
    address to,
    uint256 amount,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) external override {
    IERC20WithPermit(address(STAKED_TOKEN)).permit(
        from,
        address(this),
        amount,
        deadline,
        v,
        r,
        s
    );
    _stake(from, to, amount);
}
```
An attacker can exploit the issue by monitoring transactions in the mempool, then modifying the to ﬁeld of a stakeWithPermit() transaction. If the modiﬁed transaction is mined ﬁrst, the shares will be minted to the attacker’s address instead of the signer’s address yet the underlying tokens will be transferred from the signer’s address.

## Recommendation
Validate the to address to prevent the attack. This can be done by ensuring that to is the same address as from.
AAVE Safety Module

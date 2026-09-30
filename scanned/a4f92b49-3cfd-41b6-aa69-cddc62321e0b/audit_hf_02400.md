# [H] Improved Validation in SafeStakeNetworkV3::deposit()

## Summary
Severity: High
Contest weight: 0.5856
Dataset id: 12946
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SafeStake protocol has a key SafeStakeNetworkV3 contract manages the network-side validators and their operators. While reviewing current logic in allowing for the deposit into intended validators, we observe the logic is flawed.
To elaborate, we show below the implementation of the related deposit() routine. It basically transfers in the given amount of tokens and then updates the given set of validators. However, it does not validate the given amount for token transfer-in is equal to the sum of assigned numbers to the given set of validators. As a result, a malicious user may exploit it to increase the validator s balance and steal the funds from the contract.
```solidity
function deposit(bytes[] memory publickeys, uint256[] memory eachamounts, uint256 totalamount) external {
    _deposit(msg.sender, totalamount);
    for(uint32 index = 0; index < publickeys.length; ++index) {
        _updateValidatorBalance(publickeys[index], 0);
        _updateValidatorBalance(publickeys[index], eachamounts[index]);
    }
}
```
In addition, the accountClaimFee() routine can also be improved by validating the recovered signer is not equal to address(0).

## Recommendation
Revise the above-mentioned routines to properly validate user inputs.

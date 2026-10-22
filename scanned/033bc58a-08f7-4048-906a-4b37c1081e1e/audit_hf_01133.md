# [M] Stake function can be inhibited

## Summary
Severity: Medium
Reporter: innertia, also found by tenma
Contest weight: 0.1044
Dataset id: 4735
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _stake, there is a conditional statement `require(value == 0 || value >= minStakeAmount, "amount too small");`, where value is the following value: `uint256 value = isEth_ ? _geth.balanceOf(address(this)) : _dct.balanceOf(address(this));`.

Let's assume that the person who wants to _stake intends to pass here with the condition value == 0.

However, the attacker can front-run this and send a small token (0 < value < minStakeAmount) to this address, which will always cause the conditional statement to fail. This allows the attacker to interfere with _stake, which is an important function at the heart of the product.

## Recommendation
You can stop calculating the value based on the address balance. At the very least, consideration should be given to the fact that outsiders can increase the balance of addresses.

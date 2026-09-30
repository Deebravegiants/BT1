# [M] Validator cannot set new address if more than

## Summary
Severity: Medium
Contest weight: 0.1998
Dataset id: 22422
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a validator has more than 300 accumulated unstakes associated with it, then it cannot set a new address for itself. The only way to decrease the length of the Unstaking array is through the setValidatorAddress() function, but will revert if it's array is longer than 300 entries. A malicious delegator could stake 1,000 tokens, and then unstake 301 times with small amounts to fill up the unstaking array, and there is no way to remove those entries from the array. Every time _unstake() is called, it pushes another entry to it's array for that validator.

A malicious validator could also set it's new address to another validator, forcing a merge of information to the victim validator. The malicious validator can do this even when it's disabled with 0 tokens. So it could get to 300 length, and then send all those unstakes into another victim validators unstaking array. This is the same to other validators, effectively creating a forceful merging of them.

The README.md suggests there is a mechanism to counteract this: "In case if there are more than 300 unstakings, there is an option to transfer the address without unstakings." But there appears to be no function in scope that can transfer the address of the validator without unstakings, or any other function that can reduce the unstakings array at all.

See Summary
Validator can be permanently stuck with same address if there are too many entries in it's Unstaking array.

## Recommendation
Consider having a way to set a new address without unstakings, or allow for smaller batches to be transferred during an address change if there are too many.
Consider disallowing validators from changing their address to other validators.

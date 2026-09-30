# [M] `boreWell` can be frontrun/DoS-d

## Summary
Severity: Medium
Contest weight: 0.4136
Dataset id: 18937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `boreWell` function in the Aquifer contract is responsible for creating new Wells. However, there are two critical security issues:

1. **Stealing of user’s deposit amount** : The public readability of the `salt` parameter allows an attacker to frontrun a user’s transaction and capture the deposit amount intended for the user’s Well. By creating a Well with the same `salt` value, the attacker can receive the deposit intended for the user’s Well and withdraw the funds.
2. **DoS for`boreWell`**: Another attack vector involves an attacker deploying a Well with the same `salt` value as the user’s intended Well. This causes the user’s transaction to be reverted, resulting in a denial-of-service (DoS) attack on the `boreWell` function. The attacker can repeatedly execute this attack, preventing users from creating new Wells.

## Recommendation
To mitigate the identified security issues, it is recommended to make the upcoming Well address user-specific by combining the `salt` value with the user’s address. This ensures that each user’s Well has a unique address and prevents frontrunning attacks and DoS attacks. The following code snippet demonstrates the recommended modification:

```solidity
well = implementation.cloneDeterministic(
    keccak256(abi.encode(msg.sender, `salt`))
);
```

This issue has been addressed in the code. The `boreWell(...)` function now uses a `salt` consisting of the hash of `msg.sender` appended to the input `salt` value. 

See [here](https://github.com/BeanstalkFarms/Basin/blob/91233a22005986aa7c9f3b0c67393842cd8a8e4d/src/Aquifer.sol#L40).

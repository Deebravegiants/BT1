# [H] H-06 | Malicious Function Input In Add/Remove Leverage

## Summary
Severity: High
Contest weight: 0.2190
Dataset id: 22163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In LeverageManager, the addLeverage and removeLeverage functions allows an attacker to pass in a malicious contract as _selfLendingPairPod and _dexAdapter respectively. This opens up the surface for attacks and reentrancy. It could be used for example to avoid payment of close fees during removeLeverage: 1. Alice calls removeLeverage passing in malicious contract as _dexAdapter 2. Malicious contract is called in _swapPodForBorrowToken 3. Malicious contract does the swap with a DEX but does not return any pod tokens, instead transferring directly to Alice 4. As no pod tokens remain in LeverageManager, no close fees are applied at the end of callback and the protocol loses revenue.

## Recommendation
Perform validation on the _selfLendingPairPod and _dexAdapter inputs. Do not allow users to provide arbitrary dexAdapter addresses, and use every WeightedIndex's own immutable dexAdapter. Additionally, consider minimizing the use of arbitrary inputs in public functions, as they can expand the attack surface and introduce potential vulnerabilities, such as reentrancy risks

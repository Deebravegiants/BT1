# [M] `Repository._removeContract

## Summary
Severity: Medium
Contest weight: 0.5808
Dataset id: 18143
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the internal function that removes a contract entry from a registry. When a contract name is supplied for removal, the function first looks up the stored Contract struct, clears its address field and resets its index field to zero. Immediately afterwards it reads the index field from the same struct to determine the position of the name in the public contracts array. Because the index has already been overwritten with zero, the function always uses index 0 regardless of the actual location of the element being removed. It then copies the last element of the array into position 0 and pops the array, effectively deleting the last contract name while leaving the removed name still present in the array. This logic error corrupts the ordering of the contracts list, causing the registry to report an incorrect set of active contracts. The root cause is the premature mutation of the index state before it is used for array manipulation, a classic off‑by‑one / stale‑value bug. An attacker or any user invoking the removal routine can trigger the bug simply by calling the function with a legitimate contract name; the contract will appear to be removed in the mapping but will remain in the array, and another valid contract (typically the one at index 0) will be unintentionally erased. The impact is primarily logical: downstream components that rely on the contracts array for enumeration, permission checks, or fee distribution will operate on a malformed list, potentially leading to missing payouts, incorrect access control decisions, or user interfaces that display stale or wrong contract names. The issue manifests whenever the removal function is executed, regardless of the caller’s role, because the internal logic does not guard against the index being overwritten. All participants that interact with the registry – contract owners, protocol users, and integrators – are affected because the registry no longer provides a reliable view of active contracts. The bug was discovered during a manual code audit where the auditor noticed that the index variable was read after being set to zero, a pattern that contradicts typical Solidity array‑removal idioms. It can be hard to notice in testing because the array still contains a name, so superficial checks may think the removal succeeded, while deeper functional tests that enumerate contracts reveal the inconsistency. The correct fix is to capture the original index value before clearing the struct fields, then use that saved index to replace the removed entry with the last element and shrink the array. This aligns with the standard “swap‑and‑pop” pattern used for efficient array element deletion in Solidity, preserving array integrity and ensuring that the registry’s state remains consistent with its public view.

## Proof of Concept
`Repository._removeContract()` removes the contract name from `contracts` array.

```solidity
File: 2023-02-malt\contracts\Repository.sol
223:   function _removeContract(string memory _name) internal {
224:     bytes32 hashedName = keccak256(abi.encodePacked(_name));
225:     Contract storage currentContract = globalContracts[hashedName];
226:     currentContract.contractAddress = address(0);
227:     currentContract.index = 0;
228: 
229:     uint256 index = currentContract.index; // @audit wrong index
230:     string memory lastContract = contracts[contracts.length - 1];
231:     contracts[index] = lastContract;
232:     contracts.pop();
233:     emit RemoveContract(hashedName);
234:   }
```

But it uses the already changed index(= 0) and replaces the last name with 0 index all the time.

As a result, the contracts array will still contain the removed name and remove the valid name at index 0.

## Recommendation
We should use the original index like below.

```solidity
function _removeContract(string memory _name) internal {
  bytes32 hashedName = keccak256(abi.encodePacked(_name));
  Contract storage currentContract = globalContracts[hashedName];

  uint256 index = currentContract.index; //++++++++++++++++

  currentContract.contractAddress = address(0);
  currentContract.index = 0;

  string memory lastContract = contracts[contracts.length - 1];
  contracts[index] = lastContract;
  contracts.pop();
  emit RemoveContract(hashedName);
}
```

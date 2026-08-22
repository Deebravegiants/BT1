# [?] `Locking::__Locking_init` can be frontrun by an attacker

## Summary
Severity: Unknown
Chain: Smart contract
Component: Mento
Published: 2025-01-24
Source: https://github.com/hats-finance/Mento-0x2a1b9b1f6fa7c2e73815a7dff0e1688767382694/issues/43
Type: hats-finding

## Details
#### **Description**

Since there is no mechanism similar to `disableInitialize` in the constructor, after deploying the `Locking.sol` contract, the` __Locking_init` function can be frontrun by an attacker.
To prevent the `__Locking_init` function from being frontrun, it is recommended to add a similar `disableInitialize` mechanism in the constructor

#### **Steps To Reproduce**

1.	The project deploys the `Locking.sol` contract.
2.	The attacker calls the `__Locking_init` function before the legitimate initialization, preemptively initializing the contract.
3.	The attacker sets malicious parameters during the initialization, which can compromise the contract’s functionality and cause the project to operate incorrectly.

#### **Expected result**

After the project deploys the contract, the legitimate party should be able to call `__Locking_init` to initialize the contract properly with correct parameters.

#### **Actual result**

After deployment, the attacker can preemptively call `__Locking_init`, initializing the contract with malicious parameters and causing the project to operate improperly.

#### **Screenshots**

<!-- If applicable, add screenshots to help explain your problem. -->

#### **Additional context**

https://docs.openzeppelin.com/learn/upgrading-smart-contracts#initialization

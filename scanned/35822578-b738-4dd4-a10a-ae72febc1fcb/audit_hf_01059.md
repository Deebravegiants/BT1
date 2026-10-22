# [M] M-01 | KycWhitelist Cannot Be Deployed

## Summary
Severity: Medium
Contest weight: 0.0329
Dataset id: 4044
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a deployment‑time failure caused by the misuse of an initialization guard in the KYCWhitelist contract. The contract’s constructor calls internal functions that are protected with the onlyInitializing modifier, a guard that is part of the OpenZeppelin Initializable pattern and is intended to be active only during an explicit initializer call on upgradeable contracts. Because the contract is being deployed directly, the initializing flag is never set, so the onlyInitializing checks revert, preventing the constructor from completing and causing the whole deployment transaction to fail. This happens whenever a developer attempts to deploy the KYCWhitelist contract as a regular, non‑proxy contract, leading to a situation where the expected KYC whitelist functionality never becomes available. From a user’s point of view the deployment transaction is rejected, no contract address is created, and any UI that tries to interact with the whitelist will show errors such as “contract not found” or “deployment failed”. The impact is that the protocol cannot enforce KYC restrictions, potentially halting onboarding of new users or allowing the protocol to operate without the intended compliance layer. The issue was discovered during a manual audit that examined the constructor logic and noticed the presence of onlyInitializing on functions called from the constructor. It can be hard to notice because the Solidity compiler does not flag the misuse; the contract compiles cleanly but reverts at runtime, which may be mistaken for a network or gas‑limit problem. To fix the problem the contract should either move the initialization logic directly into the constructor (removing the onlyInitializing guard) or, if the contract is intended to be upgradeable, expose a separate external initializer function that can be called after deployment via a proxy, ensuring the initializing flag is correctly set before the guarded functions execute. In essence, the bug belongs to the class of “initializer misuse in non‑upgradeable contracts”, where deployment logic conflicts with upgradeable‑contract guards, breaking the expected deployment flow and violating the business assumption that the whitelist contract can be instantiated and used immediately after deployment.

## Recommendation
Refactor the KYCWhitelist contract so that the constructor is the initializer or make a separate initializer function.

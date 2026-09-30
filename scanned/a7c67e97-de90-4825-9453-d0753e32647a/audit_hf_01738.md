# [H] MJR-2 Controller can be initialized several times

## Summary
Severity: High
Contest weight: 0.0081
Dataset id: 9509
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a re‑initialization flaw in the Controller contract where the public initialize function can be invoked more than once. The root cause is the absence of a protection mechanism such as the OpenZeppelin initializer modifier or an explicit boolean flag that would restrict the function to a single execution. Because the contract relies on an initialize routine to set critical state variables—typically the owner, admin address, fee parameters, or other privileged settings—an attacker who discovers that the function is unrestricted can call it after deployment and overwrite those variables with attacker‑controlled values. Exploitation proceeds by sending a transaction that calls initialize with malicious arguments; the contract accepts the call, updates its storage, and effectively hands over control of the protocol logic to the attacker. The impact includes loss of administrative control, the ability to change protocol parameters arbitrarily, and potential theft or freezing of user funds, as the new controller can redirect withdrawals or disable essential functions. This condition occurs whenever the contract is deployed without a constructor and expects initialize to be called exactly once, but no guard is present to enforce that expectation. All participants that rely on the controller—protocol governance, token holders, and end‑users—are affected because the security guarantees of the system are broken. The issue was discovered during a manual audit that inspected upgradeable contract patterns and flagged the missing initializer protection as a known anti‑pattern. The flaw can be hard to notice because the initialize function may appear innocuous, emits no special events, and the contract may operate normally until an attacker triggers a re‑initialization, at which point the state change can be subtle or only observable through unexpected behavior such as sudden loss of privileges or zeroed balances. To remediate, the initialize function should be marked with the initializer modifier or wrapped in a custom one‑time guard that records whether it has already been executed and reverts on subsequent calls, thereby ensuring the initialization logic runs only once as intended.

## Recommendation
We recommend adding the initializer modifier.

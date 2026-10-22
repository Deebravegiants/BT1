# [M] Lack of Input Validation in Deposit Function will Trigger 0 Value Transactions

## Summary
Severity: Medium
Contest weight: 0.2103
Dataset id: 8806
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract’s deposit routine does not validate the amount supplied by the caller. Because the function lacks a check that the input is a numeric, positive value and also does not verify that a game session has been started before a deposit is accepted, a user can submit an empty string, zero, or arbitrary non‑numeric characters. The transaction is still sent to the blockchain, the approve button succeeds, and the contract records a deposit of zero value while consuming gas. From a technical standpoint the root cause is missing input sanitisation and missing pre‑condition enforcement, which allows the call to pass the require statements that only check for transaction success, not for logical correctness. An attacker can therefore trigger a large number of zero‑value deposits, draining gas from their own wallet or from any account that signs the transaction, and potentially creating a denial‑of‑service condition for the contract’s accounting logic because the contract may assume that every successful deposit increases a user’s balance. The issue manifests when a user interacts with the UI, sees a warning that the amount should be a positive number, but the warning is not enforced; the UI still enables the approve button and the blockchain records a transaction with value 0. This behaviour is hard to notice because the transaction appears normal on explorers – it has a successful status and a gas cost, yet no funds are transferred and the on‑chain state does not change as expected. The vulnerability was discovered during a manual audit that exercised the deposit UI with empty and malformed inputs and observed that the contract accepted the call without reverting. To remediate, the contract should enforce strict numeric validation (e.g., using require(amount > 0) and parsing the input safely), reject any non‑numeric or empty values, and add a require that a game session is active before allowing a deposit. By doing so the contract will prevent zero‑value transactions, protect users from unnecessary gas loss, and preserve the integrity of the protocol’s accounting model.

## Proof of Concept
When a user is depositing assets, the amount field is not properly sanitized to accept only numeric values. Although there is a warning message stating that the input should be a positive number, a user can still input any value (or leave it empty), triggering a zero-value transaction that only consumes gas. Moreover this transaction is occurring without Starting a game which is required before depositing an amount.

Figure 1: In the image: The current implementation allows a user to introduce special characters or an empty string, and the approve button will still process a transaction with a zero value, consuming only gas.

Figure 2: In the image: Details of the 0 value transaction from above. Although the user is required to approve this zero-value transaction, if the application warns the user to use only valid positive numbers, it should enforce this by accepting only valid input for approval.

## Recommendation
Ensure that user input is restricted to only the expected values (numbers) before allowing the approval of any transaction.

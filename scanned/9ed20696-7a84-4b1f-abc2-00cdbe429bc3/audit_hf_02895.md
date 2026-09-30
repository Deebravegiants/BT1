# [C] UBT-4 | Arbitrary Salary

## Summary
Severity: Critical
Contest weight: 0.0737
Dataset id: 16196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract permits a privileged role to modify the per‑period salary that determines how many funding tokens are transferred when a participant calls the withdraw function. Because the function that changes the salary lacks both an upper bound and proper access restrictions, an attacker can set the salary to an extremely large value. When a withdrawal is later executed, the contract calculates the amount to transfer based on this salary. The unchecked large salary either forces the contract to transfer the entire fundingToken balance, effectively draining the pool, or, during the total‑payout computation, triggers an arithmetic overflow that makes the calculated payout incorrect (often zero), preventing legitimate users from receiving their expected funds. This condition occurs whenever the salary variable is updated before a withdrawal or payout calculation. It impacts any user who expects to receive a salary payment, as they may receive nothing while the contract’s funds disappear. The issue was uncovered during a manual audit that highlighted the absence of a salary cap and insufficient access control on the salary‑setting function. Because the overflow only manifests with extreme values, it may not surface during routine testing, making it difficult to detect. The recommended remediation is to enforce a reasonable maximum salary, restrict the salary‑changing function to a trusted role (e.g., contract owner), and employ safe arithmetic (checked math) when performing payout calculations. This vulnerability belongs to the class of unbounded parameter bugs that lead to arithmetic overflow and fund drain, where unchecked user‑controlled values break accounting logic, causing funds to disappear or legitimate payouts to be blocked.

## Recommendation
Add a cap to the salary and restrict access to changeSalary.

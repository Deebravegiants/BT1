# [H] H-05 | Trapped Fees In LoopFacility

## Summary
Severity: High
Contest weight: 0.0586
Dataset id: 21898
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of trapped fees in the LoopFacility contract. The contract uses an internal function _pullReserves to collect protocol fees from users or other contracts, but the code does not provide any external or internal mechanism to transfer those collected fees to a designated recipient. The root cause is the absence of a withdrawal or fee-distribution function, which means that once fees are pulled into the contract's balance they become permanently inaccessible. An attacker does not need to perform a malicious call to exploit the bug; the impact arises automatically whenever the fee-pulling logic is executed, typically during loop operations that settle interest or rebalance positions. Under these conditions the protocol's accounting assumes that the fees will be forwarded to a fee recipient, but the actual ether or token balance remains locked inside the LoopFacility. This affects the protocol itself, its fee-receiving parties, and ultimately token holders who expect the collected fees to be used for incentives or treasury funding. The issue was discovered during a manual audit that inspected the fee handling flow and noticed that no function analogous to the setFeeRecipient function in the related CreditFacility existed. Because the contract does not emit events or provide a public view of the trapped balance, the problem can be hard to notice from the UI; users may see their transaction succeed while the protocol's treasury receives nothing, leading to a discrepancy between expected and actual fee distribution. The failure mode can be described as a “fee-locking” bug where funds disappear from the protocol's revenue stream and cannot be recovered. To remediate the issue the contract should implement a function that allows the designated fee recipient, or an authorized role, to withdraw the accumulated fees, following the same pattern used in CreditFacility. This change restores the intended accounting flow and prevents permanent loss of collected fees.

## Recommendation
Implement a function similar to the setFeeRecipient function in the CreditFacility to retrieve these fees.

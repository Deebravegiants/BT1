# [H] Bull can transferPosition() to address(0) and

## Summary
Severity: High
Contest weight: 0.1838
Dataset id: 17825
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Using bulls[uint(orderHash)] == address(0) to check whether the order is matched is insufficient, the bull can transferPosition to address(0) and the order can be matched again. An order must not be matched more than once. There is a check presented in the current implementation to prevent that: L760 require(bulls[uint(orderHash)] == address(0), "ORDER_ALREADY_MATCHED");. However, this check can be easily bypassed by the bull, as they can transferPosition() to address(0) anytime. Then the original order can be matched again. Attacker can match the orders by bear makers multiple times, pulling order.premium + bearFees from the victims' wallet as many times as they want.

## Recommendation
Consider using matchedOrders[contractId] to check if the order has been matched or not. Also, consider disallowing transferPosition() to address(0).

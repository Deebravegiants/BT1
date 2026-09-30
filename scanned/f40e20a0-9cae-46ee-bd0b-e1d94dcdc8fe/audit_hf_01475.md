# [H] H-2 Signature veriﬁcation bypass

## Summary
Severity: High
Contest weight: 0.2673
Dataset id: 7828
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• BaseRouter.sol#L271-L272
The BaseRouter._getRawData() function concatenates operations and parameters without separators. This allows a hacker to feed operations to the RouterV2.start() with different parameters while maintaining the same signature.
For example, given the operations [op1, op2] and parameters [[a, b], [c, d]], the BaseRouter._checkSignature() method cannot distinguish between [[a, b], [c, d]] and [[a], [b, c, d]] or [[a, b, c], [d]], because _getRawData() will always concatenate parameters into a single stream of [a, b, c, d].
Moreover, there will also be no errors with unpacking the parameters, because abi.decode() does not revert when provided with excess data; it discards extra bytes.
Consequently, while the backend may sign legitimate data, an attacker could reorganize this data in such a way that the operations will execute with entirely different arguments. Although this manipulation will eventually cause a revert due to missing arguments in the ﬁnal operations, an attacker could potentially extract funds prior to the revert by initiating a swap with slippage, directing funds to an emergency address controlled by the attacker.

## Recommendation
We recommend introducing separators between concatenated operations and parameters to ensure they are distinctly identiﬁable.

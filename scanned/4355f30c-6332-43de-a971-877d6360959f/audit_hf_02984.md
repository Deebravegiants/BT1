# [C] Memory alignment malleability

## Summary
Severity: Critical
Contest weight: 0.0710
Dataset id: 16629
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a memory‑alignment malleability issue caused by a constant polynomial (referred to as BYTE_C4096) that is expected to represent a single byte value in the range 0‑255 but fails to wrap around after reaching 255. Because the constant does not apply a modulo‑256 operation, the variable inV can take on values larger than a byte. When the contract later stores this value using the low‑level MSTORE8 opcode, the oversized value causes the opcode to write an extra most‑significant bit into the memory slot immediately preceding the intended byte. This off‑by‑one write corrupts the adjacent memory location, shifting data and breaking the assumed byte‑wise layout. The root cause is the missing wrap‑around (or masking) logic for the constant, which allows values outside the 8‑bit range to propagate into memory operations that are designed for single‑byte storage. An attacker can exploit this by crafting input that forces inV to exceed 255, triggering the malformed MSTORE8 write. The resulting memory corruption can alter critical state variables such as balances, counters, or cryptographic commitments, leading to incorrect accounting, unexpected zero balances, or loss of funds. The bug manifests only when the contract processes inputs that produce a value greater than 255 for the affected polynomial, which may be rare and therefore easy to miss during normal testing. Users experience symptoms such as their balance appearing unchanged after a deposit, refunds returning zero, or transaction receipts showing unexpected values. The issue was discovered during a manual security audit that inspected the handling of low‑level memory writes and identified the lack of a wrap‑around constraint. Because the problem resides in a low‑level assembly instruction, it does not generate obvious Solidity‑level errors and can remain hidden until a specific edge case is triggered. To remediate the flaw, the constant should be constrained to a byte by applying a modulo‑256 operation or by explicitly casting to uint8 before any MSTORE8 usage, ensuring that only the least‑significant 8 bits are stored. This class of bug falls under memory‑alignment or storage‑layout vulnerabilities where improper handling of byte boundaries leads to data corruption and potential financial loss.

## Recommendation
Wrap around after value 255. @@ -11,7 +11,7 @@ const CONST_F = {

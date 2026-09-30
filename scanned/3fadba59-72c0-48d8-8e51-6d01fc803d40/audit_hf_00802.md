# [M] M-03 | superPoolCap Not Implemented

## Summary
Severity: Medium
Contest weight: 0.0238
Dataset id: 2538
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing enforcement of the superPoolCap variable in the contract's deposit functions. Although the variable is initialized and can be updated, the code only references it in a read‑only view function that reports the maximum deposit amount. The actual deposit flows never check whether the accumulated pool balance would exceed the configured cap, so deposits are accepted regardless of the limit. This occurs because the developer omitted a require statement that compares the current total deposits plus the incoming amount with superPoolCap. An attacker or any user can therefore submit arbitrarily large deposits, causing the pool to grow beyond the intended maximum. The impact is that the protocol's economic assumptions about a bounded pool are broken; reward calculations, risk parameters, and token accounting that rely on the cap may become inaccurate, potentially leading to diluted rewards, unexpected token minting, or even loss of funds if later logic assumes the cap is respected. The issue manifests when a user attempts to deposit after the pool has reached the advertised limit: instead of being rejected, the transaction succeeds and the pool balance exceeds the cap, which may be visible only through the view function that still reports the old limit. All participants—depositors, token holders, and the protocol itself—are affected because the invariant that the pool size is bounded no longer holds. The flaw was discovered during a manual audit that inspected the deposit pathways and noticed the absence of any superPoolCap check. It can be hard to notice because the view function appears to enforce the limit, giving a false sense of security, and there is no on‑chain error or event indicating a violation. The correct remediation is to add explicit checks in every function that modifies the pool balance, ensuring that totalDeposits + amount does not exceed superPoolCap, and to revert the transaction with a clear error message when the limit would be breached. This brings the implementation in line with the intended business rule that the pool cannot exceed a predefined maximum.

## Recommendation
Check if the superPoolCap is reached.

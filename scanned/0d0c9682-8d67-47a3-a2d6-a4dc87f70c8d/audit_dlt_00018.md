# [H] MainnetTransactionProcessor applies SELFDESTRUCT markers from the initial frame even when the transaction fails, leaking account deletion past EIP-6780 semantics

## Summary
Severity: High
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-j2cm-8hc2-6975
Type: github-advisory

## Details
MainnetTransactionProcessor unconditionally applied initialFrame.getSelfDestructs().forEach(worldState::deleteAccount) regardless of whether the transaction succeeded. For a failed transaction, a stale selfdestruct marker leaking through could permanently delete a pre-existing account that an EIP-6780-compliant client must retain — producing a divergent post-state root from spec-compliant peers. Fixed by only applying the initial frame's selfdestructs when the transaction actually succeeded. This is a defense-in-depth fix for a depth-0 CREATE whose CREATE2->SELFDESTRUCT child leaked past a failed code deposit; the original fix's primary mechanism was superseded by public PR besu #10396 landed one day after the original private fix was authored. Fixed in Besu 26.7.1 by commit 8c7f3c1c6cc747eb9cad762307c6c37646bea709 (besu-eth/besu PR #10898).

# [M] FutureMessageBuffer bounds buffered future-height BFT messages only by count, not by byte size, allowing memory exhaustion via oversized proposals

## Summary
Severity: Medium
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-qhrf-865g-38rh
Type: github-advisory

## Details
A devp2p peer negotiating istanbul/100 could send structurally valid future-height QBFT/IBFT PROPOSAL messages carrying a multi-megabyte block, before any validator-eligibility check. FutureMessageBuffer only capped retained messages by count (futureMessagesLimit=1000), not by bytes, so ~1000 buffered multi-MB proposals could exhaust the BFT event processor's heap and halt consensus on the affected validator. This is CertiK finding HYB-02 (Major). Fixed by tracking the total byte size of buffered messages via a caller-supplied size function and evicting on a byte budget. Fixed in Besu 26.7.1 by commit 819f68c26655fa4f6797d9a5ffa825083ff156df (besu-eth/besu PR #10897). Severity critical; Probability remote.

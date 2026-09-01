# [M] Missing requestsHash presence check allows a post-Prague block header to omit the EIP-7685 requestsHash field

## Summary
Severity: Medium
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-mqqm-3pp2-ff8j
Type: github-advisory

## Details
EIP-7685 requires every post-Prague block header to carry a requestsHash field, including the empty-list hash on blocks with no execution requests. Block import previously accepted headers that omitted the field entirely, since no validation rule checked for its presence independent of the parent header — risking cross-client consensus divergence on post-Prague headers. Fixed by adding RequestsHashPresentValidationRule, wired into the Prague block header validator. Fixed in Besu 26.7.1 by commit f8abfc1042bd87f2cc8e3af7e22b1ad6e6470515 (besu-eth/besu PR #10891). Severity: Catastrophic, Probability: Remote

# [M] DKG Susceptible to Rogue Key Attack

## Summary
Severity: Medium
Contest weight: 0.0941
Dataset id: 14390
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The currently implemented Distributed Key Generation (DKG) protocol is susceptible to a rogue key attack such that, given a poorly chosen threshold parameter t, fewer than t malicious participants can collude to gain full knowledge of the shared secret. In particular, when the DKG protocol involves n members, of which any t + 1 can recover the distributed key or sign messages, n − t + 1 malicious participants can perform the rogue key attack.

## Recommendation
When choosing DKG parameters for generating and distributing the staking withdrawal key, carefully ensure that min(t + 1, n − t + 1) is above the security threshold for an acceptable number of malicious members. If a t closer to n is desired, alternative mitigations could involve a “commit-reveal” step during DKG, where all participants must publish secure hashes of their polynomial before any polynomial is revealed.

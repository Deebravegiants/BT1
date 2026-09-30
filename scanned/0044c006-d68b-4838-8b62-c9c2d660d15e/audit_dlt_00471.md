# [M] Triton VM Soundness Vulnerability due to Missing Constraint

## Summary
Severity: Medium
Chain: triton-vm
Component: triton-vm
CWE: Insufficient Verification of Data Authenticity
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-vjf8-9fx6-mv6x
Type: github-advisory

## Details
The instruction `sponge_absorb_mem` Triton VM fails to verify that hashed values come from the claimed memory location. Malicious provers can substitute arbitrary data instead of actual memory contents.

Any application using instruction `sponge_absorb_mem` to hash memory data can be given a proof for a forged hash that doesn't correspond to the actual memory. This breaks the security of memory-based commitments.

The flaw was corrected in commits `17c7ba0a` and `ef9d9e72` by including the appropriate constraints.

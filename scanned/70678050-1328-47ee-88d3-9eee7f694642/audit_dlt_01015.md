# [H] Nethermind Juno Potential Denial of Service (DoS) via Integer Overflow

## Summary
Severity: High
Chain: github.com/NethermindEth/juno
Component: github.com/NethermindEth/juno
CVE: CVE-2025-29072
CWE: Integer Overflow or Wraparound, Allocation of Resources Without Limits or Throttling
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-wq32-8rp4-w2mc
Type: github-advisory

## Details
An integer overflow in Nethermind Juno before v0.12.5 within the Sierra bytecode decompression logic within the "cairo-lang-starknet-classes" library could allow remote attackers to trigger an infinite loop (and high CPU usage) by submitting a malicious Declare v2/v3 transaction. This results in a denial-of-service condition for affected Starknet full-node implementations.

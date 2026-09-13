# [C] Incorrect Calculation in solana_rbpf

## Summary
Severity: Critical
Chain: solana_rbpf
Component: solana_rbpf
CVE: CVE-2022-23066
CWE: Incorrect Calculation
Published: 2022-05-10
Source: https://github.com/advisories/GHSA-9qmm-4mfr-r3wj
Type: github-advisory

## Details
In Solana rBPF versions 0.2.26 and 0.2.27 are affected by Incorrect Calculation which is caused by improper implementation of sdiv instruction. This can lead to the wrong execution path, resulting in huge loss in specific cases. For example, the result of a sdiv instruction may decide whether to transfer tokens or not. The vulnerability affects both integrity and may cause serious availability problems.

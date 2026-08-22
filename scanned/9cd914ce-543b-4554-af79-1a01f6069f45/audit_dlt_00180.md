# [M] btcd susceptible to consensus failures

## Summary
Severity: Medium
Chain: Bitcoin
Component: github.com/btcsuite/btcd
CVE: CVE-2024-34478
CWE: Interpretation Conflict
Published: 2024-05-05
Source: https://github.com/advisories/GHSA-3jgf-r68h-xfqm
Type: github-advisory

## Details
btcd before 0.24.0 does not correctly implement the consensus rules outlined in BIP 68 and BIP 112, making it susceptible to consensus failures. Specifically, it uses the transaction version as a signed integer when it is supposed to be treated as unsigned. There can be a chain split and loss of funds.

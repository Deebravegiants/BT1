# [M] Vyper incident: On August 6, the Ethereum compiler Vyper released an analysis report on last week's vulnerability incidents: Prior to July 30, due

## Summary
Severity: Medium
Target: Vyper
Loss: -
Attack method: Compiler Bug
Published: 2023-07-30
Source: https://hackmd.io/@vyperlang/HJUgNMhs2
Type: slowmist-incident

## Details
On August 6, the Ethereum compiler Vyper released an analysis report on last week's vulnerability incidents: Prior to July 30, due to potential vulnerabilities in the Vyper compiler, multiple Curve liquidity pools were exploited. While the bug was identified and patched, the impact on protocols using the vulnerable compiler was not recognized at the time, nor were they explicitly notified. The vulnerability itself is an improperly implemented reentrancy prevention, and the affected Vype versions are v0.2.15, v0.2.16, v0.3.0. Vulnerability fixed and tested in v0.3.1, v0.3.1 and later are safe.

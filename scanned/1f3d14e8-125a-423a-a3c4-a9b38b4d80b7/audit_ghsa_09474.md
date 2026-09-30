# [M] pyquorum: Timing side‑channel in mul_mod

## Summary
Severity: Medium
Advisory: GHSA-7r92-3jgr-r65q
CVE: CVE-2026-44368
CWE: CWE-208
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-7r92-3jgr-r65q
Type: github-advisory

## Affected
- PyPI: `pyquorum` — affected >=0 <0.2.1

## Details
### Impact
The `mul_mod` function implements multiplication via a binary expansion loop whose execution time depends on the Hamming weight of the second operand (the exponent). An attacker who can measure the time of secret‑sharing operations (e.g., via a remote service) could progressively recover the values of shares, ultimately leading to secret reconstruction.

### Patches
https://github.com/svvqt/pyquorum/releases/tag/v0.2.1

## References
- https://github.com/svvqt/pyquorum/security/advisories/GHSA-7r92-3jgr-r65q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44368
- https://github.com/svvqt/pyquorum/commit/1e9ac41dd3c305c13d7a6b7d227bf325be82d730
- https://github.com/svvqt/pyquorum
- https://github.com/svvqt/pyquorum/releases/tag/v0.2.1

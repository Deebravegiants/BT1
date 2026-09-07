# [M] FastChat open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-77cj-rv5x-v6r2
CVE: CVE-2024-10908
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-77cj-rv5x-v6r2
Type: github-advisory

## Affected
- PyPI: `fschat` — affected >=0

## Details
An open redirect vulnerability in lm-sys/fastchat Release v0.2.36 allows a remote unauthenticated attacker to redirect users to arbitrary websites via a specially crafted URL. This can be exploited for phishing attacks, malware distribution, and credential theft.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10908
- https://github.com/lm-sys/FastChat
- https://huntr.com/bounties/61f5e725-5579-4d08-8a88-e4ba04e6d1f2

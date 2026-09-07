# [M] Froxlor Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jr66-9ghf-6gp3
CVE: CVE-2023-3192
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-11
Source: https://github.com/advisories/GHSA-jr66-9ghf-6gp3
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.1.0

## Details
Versions of froxlor/froxlor prior to release 2.1.0 did not regenerate session ids appropriately which may result in session fixation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3192
- https://github.com/froxlor/froxlor/commit/94d9c3eedf31bc8447e3aa349e32880dde02ee52
- https://github.com/froxlor/froxlor
- https://huntr.dev/bounties/f3644772-9c86-4f55-a0fa-aeb11f411551

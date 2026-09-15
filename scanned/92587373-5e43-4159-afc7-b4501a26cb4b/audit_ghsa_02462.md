# [H] Uncontrolled Search Path Element in sharkdp/bat

## Summary
Severity: High
Advisory: GHSA-p24j-h477-76q3
CVE: CVE-2021-36753
CWE: CWE-427
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-p24j-h477-76q3
Type: github-advisory

## Affected
- crates.io: `bat` — affected >=0 <0.18.2

## Details
bat on windows before 0.18.2 executes programs named less.exe from the current working directory. This can lead to unintended code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36753
- https://github.com/sharkdp/bat/pull/1724
- https://github.com/sharkdp/bat/commit/bf2b2df9c9e218e35e5a38ce3d03cffb7c363956
- https://github.com/sharkdp/bat
- https://github.com/sharkdp/bat/releases/tag/v0.18.2
- https://rustsec.org/advisories/RUSTSEC-2021-0106.html
- https://vuln.ryotak.me/advisories/53

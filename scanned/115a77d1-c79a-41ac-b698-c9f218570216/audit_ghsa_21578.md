# [M] TablePress Plugin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-9mf2-hpj4-rw3r
CVE: CVE-2022-3788
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-9mf2-hpj4-rw3r
Type: github-advisory

## Affected
- Packagist: `tobiasbg/tablepress` — affected >=0

## Details
A cross-site scripting vulnerability was found in an unknown function of the component Table Import Handler. The manipulation of the argument Import data leads to cross site scripting. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3788
- https://drive.google.com/file/d/10tk6wEh1hdkb2vVoqJqZJZsOtfxpniyY/view
- https://drive.google.com/file/d/1iRUtJYUZB0Ho-2Aqyw7TCtFN9L96UDfs/view
- https://github.com/TablePress/TablePress
- https://vuldb.com/?id.212610

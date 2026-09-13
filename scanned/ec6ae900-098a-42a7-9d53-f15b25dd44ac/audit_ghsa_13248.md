# [M] gix-transport code execution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rrjw-j4m2-mf34
CVE: CVE-2023-53158
CWE: CWE-78, CWE-88
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-rrjw-j4m2-mf34
Type: github-advisory

## Affected
- crates.io: `gix-transport` — affected >=0 <0.36.1

## Details
The `gix-transport` crate prior to the patched version 0.36.1 would allow attackers to use malicious ssh clone URLs to pass arbitrary arguments to the `ssh` program, leading to arbitrary code execution.

PoC: `gix clone 'ssh://-oProxyCommand=open$IFS-aCalculator/foo'`

This will launch a calculator on OSX.

See https://secure.phabricator.com/T12961 for more details on similar vulnerabilities in `git`.

Thanks for [vin01](https://github.com/vin01) for disclosing this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-53158
- https://github.com/GitoxideLabs/gitoxide/pull/1032
- https://github.com/GitoxideLabs/gitoxide
- https://rustsec.org/advisories/RUSTSEC-2023-0064.html
- https://secure.phabricator.com/T12961

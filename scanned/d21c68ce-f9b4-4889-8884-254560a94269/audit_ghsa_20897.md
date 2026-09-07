# [M] Pimcore vulnerable to cross site scripting

## Summary
Severity: Medium
Advisory: GHSA-wqr6-57qm-hhr5
CVE: CVE-2022-3255
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-wqr6-57qm-hhr5
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.7

## Details
If an attacker can control a script that is executed in the victim's browser, then they can typically fully compromise that user. Amongst other things, the attacker can perform any action within the application that the user can perform; view any information that the user is able to view; modify any information that the user is able to modify; and/or initiate interactions with other application users, including malicious attacks, that will appear to originate from the initial victim user. A patch for this issue is available at commit 1e916e7d668c9e47b217e20cc0ea4812f466201b and anticipated to be part of version 10.5.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3255
- https://github.com/pimcore/pimcore/commit/1e916e7d668c9e47b217e20cc0ea4812f466201b
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/0ea45cf9-b256-454c-9031-2435294c0902

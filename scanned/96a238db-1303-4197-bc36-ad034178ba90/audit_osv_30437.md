# [M] eLabFTW MFA bypass

## Summary
Severity: Medium
Advisory: CVE-2024-52586
Aliases: GHSA-pvxr-39g3-m28c
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-52586
Type: osv

## Details
eLabFTW is an open source electronic lab notebook for research labs. A vulnerability has been found starting in version 4.6.0 and prior to version 5.1.0 that allows an attacker to bypass eLabFTW's built-in multifactor authentication mechanism. An attacker who can authenticate locally (by knowing or guessing the password of a user) can thus log in regardless of MFA requirements. This does not affect MFA that are performed by single sign-on services. Users are advised to upgrade to at least version 5.1.9 to receive a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52586.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-pvxr-39g3-m28c
- https://nvd.nist.gov/vuln/detail/CVE-2024-52586

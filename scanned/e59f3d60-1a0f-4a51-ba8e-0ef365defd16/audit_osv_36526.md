# [H] CVE-2026-24031

## Summary
Severity: High
Advisory: CVE-2026-24031
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-24031
Type: osv

## Details
Dovecot SQL based authentication can be bypassed when auth_username_chars is cleared by admin. This vulnerability allows bypassing authentication for any user and user enumeration. Do not clear auth_username_chars. If this is not possible, install latest fixed version. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24031.json
- https://access.redhat.com/security/cve/CVE-2026-24031
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24031.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24031
- https://bugzilla.redhat.com/show_bug.cgi?id=2452181

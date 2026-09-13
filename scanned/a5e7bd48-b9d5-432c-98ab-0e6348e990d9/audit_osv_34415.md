# [H] CVE-2025-59518

## Summary
Severity: High
Advisory: CVE-2025-59518
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-59518
Type: osv

## Details
In LemonLDAP::NG before 2.16.7 and 2.17 through 2.21 before 2.21.3, OS command injection can occur in the Safe jail. It does not Localize _ during rule evaluation. Thus, an administrator who can edit a rule evaluated by the Safe jail can execute commands on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59518.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59518
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/issues/3462
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/commit/228d01945d48015f3f9ea8a8dc64d7e6a27750e9

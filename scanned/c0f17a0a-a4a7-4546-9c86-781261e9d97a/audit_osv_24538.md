# [C] Izanami is vulnerable to Authorization Bypass

## Summary
Severity: Critical
Advisory: CVE-2023-22495
Aliases: GHSA-9r7j-m337-792c
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-14
Source: https://osv.dev/vulnerability/CVE-2023-22495
Type: osv

## Details
Izanami is a shared configuration service well-suited for micro-service architecture implementation. Attackers can bypass the authentication in this application when deployed using the official Docker image. Because a hard coded secret is used to sign the authentication token (JWT), an attacker could compromise another instance of Izanami. This issue has been patched in version 1.11.0.

## References
- https://github.com/MAIF/izanami/releases/tag/v1.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22495.json
- https://github.com/MAIF/izanami/security/advisories/GHSA-9r7j-m337-792c
- https://nvd.nist.gov/vuln/detail/CVE-2023-22495

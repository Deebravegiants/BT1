# [C] Coolify members can see private key of root user

## Summary
Severity: Critical
Advisory: CVE-2025-64420
Aliases: GHSA-qwxj-qch7-whpc
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-64420
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. In Coolify versions prior to and including v4.0.0-beta.434, low privileged users are able to see the private key of the root user on the Coolify instance. This allows them to ssh to the server and authenticate as root user, using the private key. As of time of publication, it is unclear if a patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64420.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-qwxj-qch7-whpc
- https://nvd.nist.gov/vuln/detail/CVE-2025-64420

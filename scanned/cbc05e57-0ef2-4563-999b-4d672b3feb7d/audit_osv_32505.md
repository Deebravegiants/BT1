# [C] aiven-extras allows PostgreSQL Privilege Escalation through format function

## Summary
Severity: Critical
Advisory: CVE-2025-31480
Aliases: GHSA-33xh-jqgf-6627
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-04
Source: https://osv.dev/vulnerability/CVE-2025-31480
Type: osv

## Details
aiven-extras is a PostgreSQL extension. This is a privilege escalation vulnerability, allowing elevation to superuser inside PostgreSQL databases that use the aiven-extras package. The vulnerability leverages the format function not being schema-prefixed. Affected users should install 1.1.16 and ensure they run the latest version issuing ALTER EXTENSION aiven_extras UPDATE TO '1.1.16' after installing it. This needs to happen in each database aiven_extras has been installed in.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31480.json
- https://github.com/aiven/aiven-extras/security/advisories/GHSA-33xh-jqgf-6627
- https://nvd.nist.gov/vuln/detail/CVE-2025-31480
- https://github.com/aiven/aiven-extras/commit/77b5f19a0c1d196bc741ff5c774f85fe7ca3063b

# [C] Remote Code Execution Vulnerability via SSTI in Fides Webserver Jinja Email Templating Engine

## Summary
Severity: Critical
Advisory: CVE-2024-45053
Aliases: GHSA-c34r-238x-f7qx, PYSEC-2026-1338
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-45053
Type: osv

## Details
Fides is an open-source privacy engineering platform. Starting in version 2.19.0 and prior to version 2.44.0, the Email Templating feature uses Jinja2 without proper input sanitization or rendering environment restrictions, allowing for Server-Side Template Injection that grants Remote Code Execution to privileged users. A privileged user refers to an Admin UI user with the default `Owner` or `Contributor` role, who can escalate their access and execute code on the underlying Fides Webserver container where the Jinja template rendering function is executed. The vulnerability has been patched in Fides version `2.44.0`. Users are advised to upgrade to this version or later to secure their systems against this threat. There are no workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45053.json
- https://github.com/ethyca/fides/security/advisories/GHSA-c34r-238x-f7qx
- https://nvd.nist.gov/vuln/detail/CVE-2024-45053
- https://github.com/ethyca/fides/commit/829cbd9cb5ef9c814fbac1ed6800e8d939d359c5

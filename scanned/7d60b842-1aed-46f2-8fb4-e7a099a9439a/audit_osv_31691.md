# [M] GLPI vulnerable to exposure of sensitive information in the `status.php` endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-21626
Aliases: GHSA-5vvr-pxwf-3w77
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-21626
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.71 and prior to version 10.0.18, an anonymous user can fetch sensitive information from the `status.php` endpoint. Version 10.0.18 contains a fix for the issue. Some workarounds are available. One may delete the `status.php` file, restrict its access, or remove any sensitive values from the `name` field of the active LDAP directories, mail servers authentication providers and mail receivers.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21626.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-5vvr-pxwf-3w77
- https://nvd.nist.gov/vuln/detail/CVE-2025-21626

# [M] The cloud version of the MeterSphere interface leaks some sensitive data without authentication

## Summary
Severity: Medium
Advisory: CVE-2023-38494
Aliases: GHSA-fjp5-95pv-5253
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-38494
Type: osv

## Details
MeterSphere is an open-source continuous testing platform. Prior to version 2.10.4 LTS, some interfaces of the Cloud version of MeterSphere do not have configuration permissions, and are sensitively leaked by attackers. Version 2.10.4 LTS contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38494.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-fjp5-95pv-5253
- https://nvd.nist.gov/vuln/detail/CVE-2023-38494
- https://github.com/metersphere/metersphere/commit/a23f75d93b666901fd148d834df9384f6f24cf28

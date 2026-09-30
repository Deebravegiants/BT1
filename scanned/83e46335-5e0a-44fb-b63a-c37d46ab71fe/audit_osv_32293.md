# [M] Tuleap dumps the Redis password into the generated troubleshooting archives

## Summary
Severity: Medium
Advisory: CVE-2025-27150
Aliases: GHSA-jc5r-684x-j46q
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-27150
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. The password to connect the Redis instance is not purged from the archive generated with tuleap collect-system-data. These archives are likely to be used by support teams that should not have access to this password. The vulnerability is fixed in Tuleap Community Edition 16.4.99.1740492866 and Tuleap Enterprise Edition 16.4-6 and 16.3-11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27150.json
- https://github.com/Enalean/tuleap/commit/a6702622a8db969a17522b8fac0774afdb1c916f
- https://github.com/Enalean/tuleap/security/advisories/GHSA-jc5r-684x-j46q
- https://nvd.nist.gov/vuln/detail/CVE-2025-27150
- https://tuleap.net/plugins/tracker/?aid=41870

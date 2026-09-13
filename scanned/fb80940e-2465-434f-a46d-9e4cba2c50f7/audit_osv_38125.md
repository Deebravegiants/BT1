# [M] Emlog: SQL Injection in tag_model::updateTagName() via unsanitized parameters

## Summary
Severity: Medium
Advisory: CVE-2026-34788
Aliases: GHSA-32mg-33qq-p3gf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34788
Type: osv

## Details
Emlog is an open source website building system. In versions 2.6.2 and prior, a SQL injection vulnerability exists in include/model/tag_model.php at line 168. The updateTagName() function directly interpolates user input into the SQL query string without using parameterized queries or proper escaping ($this->db->escape_string()), making it vulnerable to SQL injection attacks. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34788.json
- https://github.com/emlog/emlog/security/advisories/GHSA-32mg-33qq-p3gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34788

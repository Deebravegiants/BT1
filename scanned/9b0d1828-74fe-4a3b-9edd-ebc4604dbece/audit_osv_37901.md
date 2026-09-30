# [M] Chamilo LMS has an XML External Entity (XXE) Injection

## Summary
Severity: Medium
Advisory: CVE-2026-33737
Aliases: GHSA-c4ww-qgf2-v89j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33737
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 1.11.38 and 2.0.0-RC.3, multiple files use simplexml_load_string() without XXE protection. With LIBXML_NOENT flag, arbitrary server files can be read. This vulnerability is fixed in 1.11.38 and 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33737.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-c4ww-qgf2-v89j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33737
- https://github.com/chamilo/chamilo-lms/commit/22b1cb1c609b643765c88654155aba27070c927e
- https://github.com/chamilo/chamilo-lms/commit/af6b7002af7c15825e98fc522e2ead0d00cacaa3

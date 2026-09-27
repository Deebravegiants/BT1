# [C] Remote code execution vulnerabilities in MediaCMS

## Summary
Severity: Critical
Advisory: CVE-2024-52004
Aliases: GHSA-x3p4-4442-q2c3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-52004
Type: osv

## Details
MediaCMS is an open source video and media CMS, written in Python/Django and React, featuring a REST API. MediaCMS has been prone to vulnerabilities that upon special cases can lead to remote code execution. All versions before v4.1.0 are susceptible, and users are highly recommended to upgrade. The vulnerabilities are related with insufficient input validation while uploading media content. The condition to exploit the vulnerability is that the portal allows users to upload content. This issue has been patched in version 4.1.0. There are no known workarounds for this vulnerability.

## References
- https://github.com/mediacms-io/mediacms/blob/main/docs/admins_docs.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52004.json
- https://github.com/mediacms-io/mediacms/security/advisories/GHSA-x3p4-4442-q2c3
- https://nvd.nist.gov/vuln/detail/CVE-2024-52004

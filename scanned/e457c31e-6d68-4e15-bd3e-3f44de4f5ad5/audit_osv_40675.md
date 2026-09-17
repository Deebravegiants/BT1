# [H] Apache CXF: Denial of Service attack via large attachments

## Summary
Severity: High
Advisory: CVE-2026-54225
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-54225
Type: osv

## Details
Apache CXF allows to control the maximum attachment size via the "attachment-max-size". Prior to Apache CXF 4.2.3 and 4.1.8 and 3.6.12, there was no default placed on this size, meaning that a denial of service attack is possible if the user doesn't explicitly set the limit. Users should update to Apache CXF 4.2.3 or 4.1.8 or 3.6.12 which fixes this problem by imposing a default attachment size limit of 50mb.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/14
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54225.json
- https://lists.apache.org/thread/h2bjqm6g58z0j6893qzh728kdtk1byfy
- https://nvd.nist.gov/vuln/detail/CVE-2026-54225

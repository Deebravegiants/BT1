# [C] CVE-2022-26352

## Summary
Severity: Critical
Advisory: CVE-2022-26352
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-17
Source: https://osv.dev/vulnerability/CVE-2022-26352
Type: osv

## Details
An issue was discovered in the ContentResource API in dotCMS 3.0 through 22.02. Attackers can craft a multipart form request to post a file whose filename is not initially sanitized. This allows directory traversal, in which the file is saved outside of the intended storage location. If anonymous content creation is enabled, this allows an unauthenticated attacker to upload an executable file, such as a .jsp file, that can lead to remote code execution.

## References
- http://packetstormsecurity.com/files/167365/dotCMS-Shell-Upload.html
- https://groups.google.com/g/dotcms
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-26352
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/26xxx/CVE-2022-26352.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-26352

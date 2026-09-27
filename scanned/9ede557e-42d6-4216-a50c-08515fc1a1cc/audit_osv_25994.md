# [C] CVE-2023-49105

## Summary
Severity: Critical
Advisory: CVE-2023-49105
CVSS: 9.8 (CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:N/S:U/UI:N)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-49105
Type: osv

## Details
An issue was discovered in ownCloud owncloud/core before 10.13.1. An attacker can access, modify, or delete any file without authentication if the username of a victim is known, and the victim has no signing-key configured. This occurs because pre-signed URLs can be accepted even when no signing-key is configured for the owner of the files. The earliest affected version is 10.6.0.

## References
- https://owncloud.org/security
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-49105
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49105.json
- https://hunt.io/blog/chinese-speaking-operator-philippine-nuclear-naval-contractor
- https://nvd.nist.gov/vuln/detail/CVE-2023-49105
- https://owncloud.com/security-advisories/webdav-api-authentication-bypass-using-pre-signed-urls/

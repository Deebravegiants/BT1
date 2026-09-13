# [M] CVE-2025-61962

## Summary
Severity: Medium
Advisory: CVE-2025-61962
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-61962
Type: osv

## Details
In fetchmail before 6.5.6, the SMTP client can crash when authenticating upon receiving a 334 status code in a malformed context.

## References
- http://www.openwall.com/lists/oss-security/2025/10/04/3
- https://www.fetchmail.info/fetchmail-SA-2025-01.txt
- https://www.openwall.com/lists/oss-security/2025/10/03/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61962.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61962
- https://gitlab.com/fetchmail/fetchmail/-/commit/4c3cebfa4e659fb778ca2cae0ccb3f69201609a8

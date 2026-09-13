# [C] CVE-2021-40102

## Summary
Severity: Critical
Advisory: CVE-2021-40102
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-09-24
Source: https://osv.dev/vulnerability/CVE-2021-40102
Type: osv

## Details
An issue was discovered in Concrete CMS through 8.5.5. Arbitrary File deletion can occur via PHAR deserialization in is_dir (PHP Object Injection associated with the __wakeup magic method).

## References
- https://documentation.concretecms.org/developers/introduction/version-history/856-release-notes
- https://hackerone.com/reports/921288

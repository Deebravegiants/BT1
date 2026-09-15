# [M] CVE-2017-5541

## Summary
Severity: Medium
Advisory: CVE-2017-5541
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-01-20
Source: https://osv.dev/vulnerability/CVE-2017-5541
Type: osv

## Details
Directory traversal vulnerability in template/usererror.missing_extension.php in Symphony CMS before 2.6.10 allows remote attackers to rename arbitrary files via a .. (dot dot) in the existing-folder and new-folder parameters.

## References
- http://www.securityfocus.com/bid/95689
- https://github.com/symphonycms/symphony-2/issues/2639
- https://github.com/symphonycms/symphony-2/releases/tag/2.6.10

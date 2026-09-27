# [M] CVE-2016-10223

## Summary
Severity: Medium
Advisory: CVE-2016-10223
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-02-14
Source: https://osv.dev/vulnerability/CVE-2016-10223
Type: osv

## Details
An issue was discovered in BigTree CMS before 4.2.15. The vulnerability exists due to insufficient filtration of user-supplied data in the "id" HTTP GET parameter passed to the "core/admin/adjax/dashboard/check-module-integrity.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://github.com/bigtreecms/BigTree-CMS/blob/master/README.md
- https://github.com/bigtreecms/BigTree-CMS/commit/59ebef5978f80e2fdc7b4db4a28b668c5a39fbc3

# [H] CVE-2019-12868

## Summary
Severity: High
Advisory: CVE-2019-12868
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2019-12868
Type: osv

## Details
app/Model/Server.php in MISP 2.4.109 allows remote command execution by a super administrator because the PHP file_exists function is used with user-controlled entries, and phar:// URLs trigger deserialization.

## References
- https://zigrin.com/advisories/misp-command-injection-via-phar-deserialization/
- https://github.com/MISP/MISP/commit/c42c5fe92783dd306b7600db1f6a25324445b40c

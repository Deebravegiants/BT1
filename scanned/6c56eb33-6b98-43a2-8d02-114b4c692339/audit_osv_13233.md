# [H] CVE-2018-18737

## Summary
Severity: High
Advisory: CVE-2018-18737
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/CVE-2018-18737
Type: osv

## Details
An XXE issue was discovered in Douchat 4.0.4 because Data\notify.php calls simplexml_load_string. This can also be used for SSRF.

## References
- https://github.com/AvaterXXX/douchat/blob/master/xxe.md#xxe

# [H] CVE-2019-18850

## Summary
Severity: High
Advisory: CVE-2019-18850
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-18850
Type: osv

## Details
TrevorC2 v1.1/v1.2 fails to prevent fingerprinting primarily via a discrepancy between response headers when responding to different HTTP methods, also via predictible responses when accessing and interacting with the "SITE_PATH_QUERY".

## References
- https://github.com/trustedsec/trevorc2/blob/master/CHANGELOG.txt
- https://github.com/trustedsec/trevorc2/issues/18

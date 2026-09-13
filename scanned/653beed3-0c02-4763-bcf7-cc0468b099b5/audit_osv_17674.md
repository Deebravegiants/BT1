# [H] CVE-2020-1892

## Summary
Severity: High
Advisory: CVE-2020-1892
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-03-03
Source: https://osv.dev/vulnerability/CVE-2020-1892
Type: osv

## Details
Insufficient boundary checks when decoding JSON in JSON_parser allows read access to out of bounds memory, potentially leading to information leak and DOS. This issue affects HHVM 4.45.0, 4.44.0, 4.43.0, 4.42.0, 4.41.0, 4.40.0, 4.39.0, versions between 4.33.0 and 4.38.0 (inclusive), versions between 4.9.0 and 4.32.0 (inclusive), and versions prior to 4.8.7.

## References
- https://hhvm.com/blog/2020/02/20/security-update.html
- https://github.com/facebook/hhvm/commit/dabd48caf74995e605f1700344f1ff4a5d83441d

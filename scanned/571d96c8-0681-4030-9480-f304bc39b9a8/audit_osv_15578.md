# [H] CVE-2019-17490

## Summary
Severity: High
Advisory: CVE-2019-17490
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-10
Source: https://osv.dev/vulnerability/CVE-2019-17490
Type: osv

## Details
app\modules\polygon\controllers\ProblemController in Jiangnan Online Judge (aka jnoj) 0.8.0 allows arbitrary file upload, as demonstrated by PHP code (with a .php filename but the image/png content type) to the web/polygon/problem/tests URI.

## References
- https://github.com/shi-yang/jnoj/issues/51

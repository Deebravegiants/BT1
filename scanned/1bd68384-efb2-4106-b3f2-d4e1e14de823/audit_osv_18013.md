# [H] CVE-2020-22784

## Summary
Severity: High
Advisory: CVE-2020-22784
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-28
Source: https://osv.dev/vulnerability/CVE-2020-22784
Type: osv

## Details
In Etherpad UeberDB < 0.4.4, due to MySQL omitting trailing spaces on char / varchar columns during comparisons, retrieving database records using UeberDB's MySQL connector could allow bypassing access controls enforced on key names.

## References
- https://github.com/ether/ueberDB/commit/e8b58d03534ade8d83c2d1946a8350a23952531e

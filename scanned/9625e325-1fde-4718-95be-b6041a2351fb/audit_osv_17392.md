# [H] CVE-2020-14969

## Summary
Severity: High
Advisory: CVE-2020-14969
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-14969
Type: osv

## Details
app/Model/Attribute.php in MISP 2.4.127 lacks an ACL lookup on attribute correlations. This occurs when querying the attribute restsearch API, revealing metadata about a correlating but unreachable attribute.

## References
- https://github.com/MISP/MISP/commit/609bfbd450c933d21c50c9f0161d633c43413eb6

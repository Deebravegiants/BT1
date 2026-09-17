# [H] CVE-2021-31780

## Summary
Severity: High
Advisory: CVE-2021-31780
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-23
Source: https://osv.dev/vulnerability/CVE-2021-31780
Type: osv

## Details
In app/Model/MispObject.php in MISP 2.4.141, an incorrect sharing group association could lead to information disclosure on an event edit. When an object has a sharing group associated with an event edit, the sharing group object is ignored and instead the passed local ID is reused.

## References
- https://github.com/MISP/MISP/commit/a0f08501d2850025892e703f40fb1570c7995478

# [C] CVE-2021-25992

## Summary
Severity: Critical
Advisory: CVE-2021-25992
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-10
Source: https://osv.dev/vulnerability/CVE-2021-25992
Type: osv

## Details
In Ifme, versions 1.0.0 to v.7.33.2 don’t properly invalidate a user’s session even after the user initiated logout. It makes it possible for an attacker to reuse the admin cookies either via local/network access or by other hypothetical attacks.

## References
- https://github.com/ifmeorg/ifme/commit/014f6d3526a594109d4d6607c2f30b1865e37611
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25992

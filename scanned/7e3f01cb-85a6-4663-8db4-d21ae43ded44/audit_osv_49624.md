# [M] CVE-2019-14826

## Summary
Severity: Medium
Advisory: CVE-2019-14826
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-17
Source: https://osv.dev/vulnerability/CVE-2019-14826
Type: osv

## Details
A flaw was found in FreeIPA versions 4.5.0 and later. Session cookies were retained in the cache after logout. An attacker could abuse this flaw if they obtain previously valid session cookies and can use this to gain access to the session.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14826

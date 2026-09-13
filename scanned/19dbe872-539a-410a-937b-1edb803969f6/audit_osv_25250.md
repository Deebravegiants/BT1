# [M] CVE-2023-32636

## Summary
Severity: Medium
Advisory: CVE-2023-32636
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-14
Source: https://osv.dev/vulnerability/CVE-2023-32636
Type: osv

## Details
A flaw was found in glib, where the gvariant deserialization code is vulnerable to a denial of service introduced by additional input validation added to resolve CVE-2023-29499. The offset table validation may be very slow. This bug does not affect any released version of glib but does affect glib distributors who followed the guidance of glib developers to backport the initial fix for CVE-2023-29499.

## References
- https://https://discourse.gnome.org/t/multiple-fixes-for-gvariant-normalisation-issues-in-glib/12835
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32636.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32636
- https://security.netapp.com/advisory/ntap-20231110-0002/
- https://gitlab.gnome.org/GNOME/glib/-/issues/2841

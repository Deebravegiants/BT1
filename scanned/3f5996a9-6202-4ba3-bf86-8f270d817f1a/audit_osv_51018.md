# [C] CVE-2020-9366

## Summary
Severity: Critical
Advisory: CVE-2020-9366
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/CVE-2020-9366
Type: osv

## Details
A buffer overflow was found in the way GNU Screen before 4.8.0 treated the special escape OSC 49. Specially crafted output, or a special program, could corrupt memory and crash Screen or possibly have unspecified other impact.

## References
- http://www.openwall.com/lists/oss-security/2020/02/25/1
- https://security.gentoo.org/glsa/202003-62
- https://lists.gnu.org/archive/html/screen-devel/2020-02/msg00007.html
- https://www.openwall.com/lists/oss-security/2020/02/06/3

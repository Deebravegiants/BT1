# [M] CVE-2021-3605

## Summary
Severity: Medium
Advisory: CVE-2021-3605
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-25
Source: https://osv.dev/vulnerability/CVE-2021-3605
Type: osv

## Details
There's a flaw in OpenEXR's rleUncompress functionality in versions prior to 3.0.5. An attacker who is able to submit a crafted file to an application linked with OpenEXR could cause an out-of-bounds read. The greatest risk from this flaw is to application availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202210-31
- https://www.debian.org/security/2022/dsa-5299
- https://bugzilla.redhat.com/show_bug.cgi?id=1970991

# [M] JLSEC-2026-128

## Summary
Severity: Medium
Advisory: JLSEC-2026-128
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-128
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=0 <3.1.1+0

## Details
There's a flaw in OpenEXR's ImfDeepScanLineInputFile functionality in versions prior to 3.0.5. An attacker who is able to submit a crafted file to an application linked with OpenEXR could cause an out-of-bounds read. The greatest risk from this flaw is to application availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1970987
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202210-31
- https://www.debian.org/security/2022/dsa-5299

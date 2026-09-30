# [H] CVE-2021-30500

## Summary
Severity: High
Advisory: CVE-2021-30500
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-30500
Type: osv

## Details
Null pointer dereference was found in upx PackLinuxElf::canUnpack() in p_lx_elf.cpp,in version UPX 4.0.0. That allow attackers to execute arbitrary code and cause a denial of service via a crafted file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1948692
- https://github.com/upx/upx/issues/485
- https://github.com/upx/upx/commit/90279abdfcd235172eab99651043051188938dcc

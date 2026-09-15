# [H] CVE-2021-20294

## Summary
Severity: High
Advisory: CVE-2021-20294
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-20294
Type: osv

## Details
A flaw was found in binutils readelf 2.35 program. An attacker who is able to convince a victim using readelf to read a crafted file could trigger a stack buffer overflow, out-of-bounds write of arbitrary data supplied by the attacker. The highest impact of this flaw is to confidentiality, integrity, and availability.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://sourceware.org/git/?p=binutils-gdb.git%3Ba=patch%3Bh=372dd157272e0674d13372655cc60eaca9c06926
- https://security.gentoo.org/glsa/202208-30
- https://bugzilla.redhat.com/show_bug.cgi?id=1943533
- https://sourceware.org/bugzilla/show_bug.cgi?id=26929

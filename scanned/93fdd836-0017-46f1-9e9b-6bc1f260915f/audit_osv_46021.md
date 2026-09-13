# [M] JLSEC-2026-579

## Summary
Severity: Medium
Advisory: JLSEC-2026-579
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-579
Type: osv

## Affected
- Julia: `XSLT_jll` — affected >=0 <1.1.34+0

## Details
In numbers.c in libxslt 1.1.33, a type holding grouping characters of an xsl:number instruction was too narrow and an invalid character/length combination could be passed to xsltNumberFormatDecimal, leading to a read of uninitialized stack data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00062.html
- http://seclists.org/fulldisclosure/2019/Aug/11
- http://seclists.org/fulldisclosure/2019/Aug/13
- http://seclists.org/fulldisclosure/2019/Aug/14
- http://seclists.org/fulldisclosure/2019/Aug/15
- http://seclists.org/fulldisclosure/2019/Jul/22
- http://seclists.org/fulldisclosure/2019/Jul/23
- http://seclists.org/fulldisclosure/2019/Jul/24
- http://seclists.org/fulldisclosure/2019/Jul/26
- http://seclists.org/fulldisclosure/2019/Jul/31
- http://seclists.org/fulldisclosure/2019/Jul/37
- http://seclists.org/fulldisclosure/2019/Jul/38
- http://www.openwall.com/lists/oss-security/2019/11/17/2
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15069
- https://gitlab.gnome.org/GNOME/libxslt/commit/6ce8de69330783977dd14f6569419489875fb71b
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2019/07/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IOYJKXPQCUNBMMQJWYXOR6QRUJZHEDRZ/
- https://oss-fuzz.com/testcase-detail/5197371471822848

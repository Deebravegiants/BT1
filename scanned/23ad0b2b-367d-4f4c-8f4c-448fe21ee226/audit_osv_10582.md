# [C] CVE-2017-17484

## Summary
Severity: Critical
Advisory: CVE-2017-17484
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-10
Source: https://osv.dev/vulnerability/CVE-2017-17484
Type: osv

## Details
The ucnv_UTF8FromUTF8 function in ucnv_u8.cpp in International Components for Unicode (ICU) for C/C++ through 60.1 mishandles ucnv_convertEx calls for UTF-8 to UTF-8 conversion, which allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted string, as demonstrated by ZNC.

## References
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://github.com/znc/znc/issues/1459
- https://ssl.icu-project.org/trac/changeset/40715
- https://ssl.icu-project.org/trac/ticket/13490
- https://ssl.icu-project.org/trac/ticket/13510
- https://ssl.icu-project.org/trac/changeset/40714
- https://ssl.icu-project.org/trac/attachment/ticket/13490/poc.cpp

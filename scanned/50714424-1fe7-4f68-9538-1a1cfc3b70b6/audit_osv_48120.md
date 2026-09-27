# [M] CVE-2017-18237

## Summary
Severity: Medium
Advisory: CVE-2017-18237
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18237
Type: osv

## Details
An issue was discovered in Exempi before 2.4.3. The PostScript_Support::ConvertToDate function in XMPFiles/source/FormatSupport/PostScript_Support.cpp allows remote attackers to cause a denial of service (invalid pointer dereference and application crash) via a crafted .ps file.

## References
- https://cgit.freedesktop.org/exempi/commit/?id=f19d0107fbae1fb41836cd110d4425e407e64048
- https://bugs.freedesktop.org/show_bug.cgi?id=101914

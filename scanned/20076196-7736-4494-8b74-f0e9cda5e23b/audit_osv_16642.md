# [H] CVE-2019-8382

## Summary
Severity: High
Advisory: CVE-2019-8382
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8382
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-628. A NULL pointer dereference occurs in the function AP4_List:Find located in Core/Ap4List.h when called from Core/Ap4Movie.cpp. It can be triggered by sending a crafted file to the mp4dump binary. It allows an attacker to cause a Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://github.com/axiomatic-systems/Bento4/issues/364
- https://research.loginsoft.com/bugs/null-pointer-dereference-vulnerability-in-function-ap4_listfind-bento4-1-5-1-628/

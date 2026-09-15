# [M] CVE-2020-23912

## Summary
Severity: Medium
Advisory: CVE-2020-23912
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23912
Type: osv

## Details
An issue was discovered in Bento4 through v1.6.0-637. A NULL pointer dereference exists in the function AP4_StszAtom::GetSampleSize() located in Ap4StszAtom.cpp. It allows an attacker to cause Denial of Service.

## References
- https://github.com/axiomatic-systems/Bento4/issues/540

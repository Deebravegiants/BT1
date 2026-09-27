# [H] CVE-2020-23330

## Summary
Severity: High
Advisory: CVE-2020-23330
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-17
Source: https://osv.dev/vulnerability/CVE-2020-23330
Type: osv

## Details
An issue was discovered in Bento4 version 06c39d9. A NULL pointer dereference exists in the AP4_Stz2Atom::GetSampleSize component located in /Core/Ap4Stz2Atom.cpp. It allows an attacker to cause a denial of service (DOS).

## References
- https://github.com/axiomatic-systems/Bento4/issues/511

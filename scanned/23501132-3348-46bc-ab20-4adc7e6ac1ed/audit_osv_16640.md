# [H] CVE-2019-8380

## Summary
Severity: High
Advisory: CVE-2019-8380
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8380
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-628. A NULL pointer dereference occurs in AP4_Track::GetSampleIndexForTimeStampMs() located in Core/Ap4Track.cpp. It can triggered by sending a crafted file to the mp4audioclip binary. It allows an attacker to cause a Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://github.com/axiomatic-systems/Bento4/issues/366
- https://research.loginsoft.com/bugs/null-pointer-dereference-vulnerability-in-function-ap4_trackgetsampleindexfortimestampms-bento4-1-5-1-628/

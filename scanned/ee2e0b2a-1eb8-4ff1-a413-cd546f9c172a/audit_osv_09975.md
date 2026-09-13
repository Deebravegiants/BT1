# [M] CVE-2017-12474

## Summary
Severity: Medium
Advisory: CVE-2017-12474
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-06
Source: https://osv.dev/vulnerability/CVE-2017-12474
Type: osv

## Details
The AP4_AtomSampleTable::GetSample function in Core/Ap4AtomSampleTable.cpp in Bento4 mp42ts before 1.5.0-616 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted mp4 file.

## References
- https://drive.google.com/open?id=0B6wBkDmxMGMKUjNscThnbTlSZ2s
- https://drive.google.com/open?id=0B9DojFnTUSNGZ1JfNUc1am9pcnc
- https://github.com/axiomatic-systems/Bento4/commit/4d3f0bebd5f8518fd775f671c12bea58c68e814e

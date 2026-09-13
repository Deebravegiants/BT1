# [H] CVE-2023-5679

## Summary
Severity: High
Advisory: CVE-2023-5679
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2023-5679
Type: osv

## Details
A bad interaction between DNS64 and serve-stale may cause `named` to crash with an assertion failure during recursive resolution, when both of these features are enabled.
This issue affects BIND 9 versions 9.16.12 through 9.16.45, 9.18.0 through 9.18.21, 9.19.0 through 9.19.19, 9.16.12-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- http://www.openwall.com/lists/oss-security/2024/02/13/1
- https://kb.isc.org/docs/cve-2023-5679
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVRDSJVZKMCXKKPP6PNR62T7RWZ3YSDZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PNNHZSZPG2E7NBMBNYPGHCFI4V4XRWNQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGS7JN6FZXUSTC2XKQHH27574XOULYYJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZDZFMEKQTZ4L7RY46FCENWFB5MDT263R/
- https://security.netapp.com/advisory/ntap-20240426-0002/

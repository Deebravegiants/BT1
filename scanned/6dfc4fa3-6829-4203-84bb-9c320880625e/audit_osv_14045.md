# [C] CVE-2018-6548

## Summary
Severity: Critical
Advisory: CVE-2018-6548
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6548
Type: osv

## Details
A use-after-free issue was discovered in libwebm through 2018-02-02. If a Vp9HeaderParser was initialized once before, its property frame_ would not be changed because of code in vp9parser::Vp9HeaderParser::SetFrame. Its frame_ could be freed while the corresponding pointer would not be updated, leading to a dangling pointer. This is related to the function OutputCluster in webm_info.cc.

## References
- https://bugs.chromium.org/p/webm/issues/detail?id=1493
- https://github.com/dwfault/PoCs/blob/master/libwebm%20Vp9HeaderParser%20UAF%20by%20PrintVP9Info/libwebm%20Vp9HeaderParser%20UAF%20by%20PrintVP9Info.md

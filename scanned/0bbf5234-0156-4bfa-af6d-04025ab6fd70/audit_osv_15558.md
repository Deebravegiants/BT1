# [C] CVE-2019-17192

## Summary
Severity: Critical
Advisory: CVE-2019-17192
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-05
Source: https://osv.dev/vulnerability/CVE-2019-17192
Type: osv

## Details
The WebRTC component in the Signal Private Messenger application through 4.47.7 for Android processes videoconferencing RTP packets before a callee chooses to answer a call, which might make it easier for remote attackers to cause a denial of service or possibly have unspecified other impact via malformed packets. NOTE: the vendor plans to continue this behavior for performance reasons unless a WebRTC design change occurs

## References
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1936
- https://news.ycombinator.com/item?id=21161432
- https://twitter.com/moxie/status/1180226374851710976

# [H] CVE-2019-17191

## Summary
Severity: High
Advisory: CVE-2019-17191
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-05
Source: https://osv.dev/vulnerability/CVE-2019-17191
Type: osv

## Details
The Signal Private Messenger application before 4.47.7 for Android allows a caller to force a call to be answered, without callee user interaction, via a connect message. The existence of the call is noticeable to the callee; however, the audio channel may be open before the callee can block eavesdropping.

## References
- https://twitter.com/moxie/status/1180261210341511168
- https://news.ycombinator.com/item?id=21161432
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1943

# [C] CVE-2020-13901

## Summary
Severity: Critical
Advisory: CVE-2020-13901
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-10
Source: https://osv.dev/vulnerability/CVE-2020-13901
Type: osv

## Details
An issue was discovered in janus-gateway (aka Janus WebRTC Server) through 0.10.0. janus_sdp_merge in sdp.c has a stack-based buffer overflow.

## References
- https://github.com/meetecho/janus-gateway/blob/v0.10.0/sdp.c#L1248
- https://github.com/meetecho/janus-gateway/pull/2214
- https://github.com/merrychap/poc_exploits/tree/master/janus-webrtc/CVE-2020-13901

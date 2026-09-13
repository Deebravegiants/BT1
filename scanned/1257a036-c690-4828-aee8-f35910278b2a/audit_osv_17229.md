# [H] CVE-2020-13898

## Summary
Severity: High
Advisory: CVE-2020-13898
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-10
Source: https://osv.dev/vulnerability/CVE-2020-13898
Type: osv

## Details
An issue was discovered in janus-gateway (aka Janus WebRTC Server) through 0.10.0. janus_sdp_process in sdp.c has a NULL pointer dereference.

## References
- https://github.com/meetecho/janus-gateway/blob/v0.10.0/sdp.c#L120
- https://github.com/meetecho/janus-gateway/blob/v0.10.0/sdp.c#L123
- https://github.com/meetecho/janus-gateway/pull/2214
- https://github.com/merrychap/CVEs/tree/master/janus-webrtc/CVE-2020-13898

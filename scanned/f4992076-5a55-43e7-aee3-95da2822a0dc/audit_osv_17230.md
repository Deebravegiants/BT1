# [H] CVE-2020-13899

## Summary
Severity: High
Advisory: CVE-2020-13899
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-10
Source: https://osv.dev/vulnerability/CVE-2020-13899
Type: osv

## Details
An issue was discovered in janus-gateway (aka Janus WebRTC Server) through 0.10.0. janus_process_incoming_request in janus.c discloses information from uninitialized stack memory.

## References
- https://github.com/meetecho/janus-gateway/blob/v0.10.0/janus.c#L1326
- https://github.com/meetecho/janus-gateway/pull/2214
- https://github.com/merrychap/poc_exploits/tree/master/janus-webrtc/CVE-2020-13899

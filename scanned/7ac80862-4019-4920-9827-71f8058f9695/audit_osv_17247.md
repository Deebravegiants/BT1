# [C] CVE-2020-14033

## Summary
Severity: Critical
Advisory: CVE-2020-14033
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14033
Type: osv

## Details
An issue was discovered in janus-gateway (aka Janus WebRTC Server) through 0.10.0. janus_streaming_rtsp_parse_sdp in plugins/janus_streaming.c has a Buffer Overflow via a crafted RTSP server.

## References
- https://github.com/meetecho/janus-gateway/pull/2229
- https://github.com/meetecho/janus-gateway/blob/v0.10.0/plugins/janus_streaming.c#L6117
- https://github.com/meetecho/janus-gateway/blob/v0.10.0/plugins/janus_streaming.c#L6166

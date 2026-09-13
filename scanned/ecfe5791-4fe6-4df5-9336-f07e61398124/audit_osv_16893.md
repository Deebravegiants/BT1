# [H] CVE-2020-10573

## Summary
Severity: High
Advisory: CVE-2020-10573
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-14
Source: https://osv.dev/vulnerability/CVE-2020-10573
Type: osv

## Details
An issue was discovered in Janus through 0.9.1. janus_audiobridge.c has a double mutex unlock when listing private rooms in AudioBridge.

## References
- https://github.com/meetecho/janus-gateway/pull/1988

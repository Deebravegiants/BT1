# [M] CVE-2020-10576

## Summary
Severity: Medium
Advisory: CVE-2020-10576
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-14
Source: https://osv.dev/vulnerability/CVE-2020-10576
Type: osv

## Details
An issue was discovered in Janus through 0.9.1. plugins/janus_voicemail.c in the VoiceMail plugin has a race condition that could cause a server crash.

## References
- https://github.com/meetecho/janus-gateway/pull/1993

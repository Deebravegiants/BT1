# [C] CVE-2020-10574

## Summary
Severity: Critical
Advisory: CVE-2020-10574
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-14
Source: https://osv.dev/vulnerability/CVE-2020-10574
Type: osv

## Details
An issue was discovered in Janus through 0.9.1. janus.c tries to use a string that doesn't actually exist during a "query_logger" Admin API request, because of a typo in the JSON validation.

## References
- https://github.com/meetecho/janus-gateway/pull/1989

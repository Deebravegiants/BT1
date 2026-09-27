# [H] CVE-2017-7523

## Summary
Severity: High
Advisory: CVE-2017-7523
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-21
Source: https://osv.dev/vulnerability/CVE-2017-7523
Type: osv

## Details
Cygwin versions 1.7.2 up to and including 1.8.0 are vulnerable to buffer overflow vulnerability in wcsxfrm/wcsxfrm_l functions resulting into denial-of-service by crashing the process or potential hijack of the process running with administrative privileges triggered by specially crafted input string.

## References
- https://cygwin.com/ml/cygwin/2017-05/msg00149.html

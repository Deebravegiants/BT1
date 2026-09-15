# [M] CVE-2018-1000021

## Summary
Severity: Medium
Advisory: CVE-2018-1000021
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000021
Type: osv

## Details
GIT version 2.15.1 and earlier contains a Input Validation Error vulnerability in Client that can result in problems including messing up terminal configuration to RCE. This attack appear to be exploitable via The user must interact with a malicious git server, (or have their traffic modified in a MITM attack).

## References
- http://www.batterystapl.es/2018/01/security-implications-of-ansi-escape.html

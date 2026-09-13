# [C] CVE-2021-39497

## Summary
Severity: Critical
Advisory: CVE-2021-39497
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-39497
Type: osv

## Details
eyoucms 1.5.4 lacks sanitization of input data, allowing an attacker to inject a url to trigger blind SSRF via the saveRemote() function.

## References
- http://hptcybersec.com/ssrf_PoC.jpg
- https://github.com/eyoucms/eyoucms/releases/tag/v1.5.4
- https://github.com/KietNA-HPT/CVE

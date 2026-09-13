# [C] CVE-2017-16926

## Summary
Severity: Critical
Advisory: CVE-2017-16926
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/CVE-2017-16926
Type: osv

## Details
Ohcount 3.0.0 is prone to a command injection via specially crafted filenames containing shell metacharacters, which can be exploited by an attacker (providing a source tree for Ohcount processing) to execute arbitrary code as the user running Ohcount.

## References
- https://bugs.debian.org/882372

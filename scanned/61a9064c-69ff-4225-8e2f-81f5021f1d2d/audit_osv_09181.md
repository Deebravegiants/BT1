# [M] CVE-2016-8734

## Summary
Severity: Medium
Advisory: CVE-2016-8734
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2016-8734
Type: osv

## Details
Apache Subversion's mod_dontdothat module and HTTP clients 1.4.0 through 1.8.16, and 1.9.0 through 1.9.4 are vulnerable to a denial-of-service attack caused by exponential XML entity expansion. The attack can cause the targeted process to consume an excessive amount of CPU resources or memory.

## References
- https://lists.apache.org/thread.html/7798f5cda1b2a3c70db4be77694b12dec8fcc1a441b00009d44f0e09%40%3Cannounce.apache.org%3E
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://www.debian.org/security/2017/dsa-3932
- http://www.securityfocus.com/bid/94588
- http://www.securitytracker.com/id/1037361
- https://subversion.apache.org/security/CVE-2016-8734-advisory.txt

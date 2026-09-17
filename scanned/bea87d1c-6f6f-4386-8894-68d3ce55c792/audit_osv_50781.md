# [H] CVE-2020-6097

## Summary
Severity: High
Advisory: CVE-2020-6097
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-10
Source: https://osv.dev/vulnerability/CVE-2020-6097
Type: osv

## Details
An exploitable denial of service vulnerability exists in the atftpd daemon functionality of atftp 0.7.git20120829-3.1+b1. A specially crafted sequence of RRQ-Multicast requests trigger an assert() call resulting in denial-of-service. An attacker can send a sequence of malicious packets to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00058.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00014.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1029

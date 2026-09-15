# [H] CVE-2019-15719

## Summary
Severity: High
Advisory: CVE-2019-15719
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-15719
Type: osv

## Details
Altair PBS Professional through 19.1.2 allows Privilege Escalation because an attacker can send a message directly to pbs_mom, which fails to properly authenticate the message. This results in code execution as an arbitrary user.

## References
- https://www.pbspro.org/
- https://www.hpcsec.com
- http://packetstormsecurity.com/files/154782/PBS-Professional-19.2.3-Authentication-Bypass.html
- https://www.hpcsec.com/2019/10/08/cve-2019-15719/

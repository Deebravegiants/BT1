# [H] CVE-2017-14461

## Summary
Severity: High
Advisory: CVE-2017-14461
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2017-14461
Type: osv

## Details
A specially crafted email delivered over SMTP and passed on to Dovecot by MTA can trigger an out of bounds read resulting in potential sensitive information disclosure and denial of service. In order to trigger this vulnerability, an attacker needs to send a specially crafted email message to the server.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00036.html
- https://usn.ubuntu.com/3587-2/
- http://www.securityfocus.com/bid/103201
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0510
- https://www.debian.org/security/2018/dsa-4130
- https://www.dovecot.org/list/dovecot-news/2018-February/000370.html
- https://usn.ubuntu.com/3587-1/

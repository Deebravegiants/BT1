# [M] CVE-2018-13441

## Summary
Severity: Medium
Advisory: CVE-2018-13441
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-12
Source: https://osv.dev/vulnerability/CVE-2018-13441
Type: osv

## Details
qh_help in Nagios Core version 4.4.1 and earlier is prone to a NULL pointer dereference vulnerability, which allows attacker to cause a local denial-of-service condition by sending a crafted payload to the listening UNIX socket.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00022.html
- https://knowledge.opsview.com/v5.3/docs/whats-new
- https://knowledge.opsview.com/v5.4/docs/whats-new
- https://gist.github.com/fakhrizulkifli/8df4a174158df69ebd765f824bd736b8
- https://www.exploit-db.com/exploits/45082/

# [M] CVE-2018-13457

## Summary
Severity: Medium
Advisory: CVE-2018-13457
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-12
Source: https://osv.dev/vulnerability/CVE-2018-13457
Type: osv

## Details
qh_echo in Nagios Core 4.4.1 and earlier is prone to a NULL pointer dereference vulnerability, which allows attackers to cause a local denial-of-service condition by sending a crafted payload to the listening UNIX socket.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00022.html
- https://knowledge.opsview.com/v5.3/docs/whats-new
- https://knowledge.opsview.com/v5.4/docs/whats-new
- https://gist.github.com/fakhrizulkifli/87cf1c1ad403b4d40a86d90c9c9bf7ab
- https://www.exploit-db.com/exploits/45082/

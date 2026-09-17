# [H] CVE-2017-15908

## Summary
Severity: High
Advisory: CVE-2017-15908
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-26
Source: https://osv.dev/vulnerability/CVE-2017-15908
Type: osv

## Details
In systemd 223 through 235, a remote DNS server can respond with a custom crafted DNS NSEC resource record to trigger an infinite loop in the dns_packet_read_type_window() function of the 'systemd-resolved' service and cause a DoS of the affected service.

## References
- http://www.securityfocus.com/bid/101600
- http://www.securitytracker.com/id/1039662
- https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1725351
- https://github.com/systemd/systemd/pull/7184
- https://usn.ubuntu.com/3558-1/

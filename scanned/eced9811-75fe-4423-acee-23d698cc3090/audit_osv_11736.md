# [H] CVE-2017-9445

## Summary
Severity: High
Advisory: CVE-2017-9445
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-28
Source: https://osv.dev/vulnerability/CVE-2017-9445
Type: osv

## Details
In systemd through 233, certain sizes passed to dns_packet_new in systemd-resolved can cause it to allocate a buffer that's too small. A malicious DNS server can exploit this via a response with a specially crafted TCP payload to trick systemd-resolved into allocating a buffer that's too small, and subsequently write arbitrary data beyond the end of it.

## References
- https://launchpad.net/bugs/1695546
- http://www.securityfocus.com/bid/99302
- http://www.securitytracker.com/id/1038806
- http://openwall.com/lists/oss-security/2017/06/27/8

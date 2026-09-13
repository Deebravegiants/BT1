# [H] CVE-2017-3144

## Summary
Severity: High
Advisory: CVE-2017-3144
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2017-3144
Type: osv

## Details
A vulnerability stemming from failure to properly clean up closed OMAPI connections can lead to exhaustion of the pool of socket descriptors available to the DHCP server. Affects ISC DHCP 4.1.0 to 4.1-ESV-R15, 4.2.0 to 4.2.8, 4.3.0 to 4.3.6. Older versions may also be affected but are well beyond their end-of-life (EOL). Releases prior to 4.1.0 have not been tested.

## References
- http://www.securityfocus.com/bid/102726
- http://www.securitytracker.com/id/1040194
- https://access.redhat.com/errata/RHSA-2018:0158
- https://kb.isc.org/docs/aa-01541
- https://usn.ubuntu.com/3586-1/
- https://www.debian.org/security/2018/dsa-4133

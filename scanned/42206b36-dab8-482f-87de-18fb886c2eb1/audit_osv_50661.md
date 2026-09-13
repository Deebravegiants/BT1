# [H] CVE-2020-27569

## Summary
Severity: High
Advisory: CVE-2020-27569
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-27569
Type: osv

## Details
Arbitrary File Write exists in Aviatrix VPN Client 2.8.2 and earlier. The VPN service writes logs to a location that is world writable and can be leveraged to gain write access to any file on the system.

## References
- https://docs.aviatrix.com/HowTos/security_bulletin_article.html#openvpn-abitrary-file-write

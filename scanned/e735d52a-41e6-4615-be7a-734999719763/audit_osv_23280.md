# [H] CVE-2022-46770

## Summary
Severity: High
Advisory: CVE-2022-46770
Aliases: OSEC-2022-01
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-07
Source: https://osv.dev/vulnerability/CVE-2022-46770
Type: osv

## Details
qubes-mirage-firewall (aka Mirage firewall for QubesOS) 0.8.x through 0.8.3 allows guest OS users to cause a denial of service (CPU consumption and loss of forwarding) via a crafted multicast UDP packet (IP address range of 224.0.0.0 through 239.255.255.255).

## References
- http://packetstormsecurity.com/files/171610/Qubes-Mirage-Firewall-0.8.3-Denial-Of-Service.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46770.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46770
- https://github.com/mirage/qubes-mirage-firewall/issues/166

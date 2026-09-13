# [H] CVE-2023-30463

## Summary
Severity: High
Advisory: CVE-2023-30463
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-30463
Type: osv

## Details
Altran picoTCP through 1.7.0 allows memory corruption (and subsequent denial of service) because of an integer overflow in pico_ipv6_alloc when processing large ICMPv6 packets. This affects installations with Ethernet support in which a packet size greater than 65495 may occur.

## References
- https://georgyg.com/home/picotcp-denial-of-service-cve-2023-30463/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30463.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30463
- https://github.com/tass-belgium/picotcp/releases

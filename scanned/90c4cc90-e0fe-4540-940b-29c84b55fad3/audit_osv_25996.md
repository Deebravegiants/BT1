# [H] CVE-2023-49203

## Summary
Severity: High
Advisory: CVE-2023-49203
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2023-49203
Type: osv

## Details
Technitium 11.5.3 allows remote attackers to cause a denial of service (bandwidth amplification) because the DNSBomb manipulation causes accumulation of low-rate DNS queries such that there is a large-sized response in a burst of traffic.

## References
- https://gist.github.com/idealeer/89947ca07836fd0f7e9761198ca9a0f3.
- https://technitium.com/dns/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49203.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49203

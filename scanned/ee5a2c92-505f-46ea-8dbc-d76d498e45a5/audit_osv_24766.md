# [H] CVE-2023-26249

## Summary
Severity: High
Advisory: CVE-2023-26249
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-21
Source: https://osv.dev/vulnerability/CVE-2023-26249
Type: osv

## Details
Knot Resolver before 5.6.0 enables attackers to consume its resources, launching amplification attacks and potentially causing a denial of service. Specifically, a single client query may lead to a hundred TCP connection attempts if a DNS server closes connections without providing a response.

## References
- https://www.knot-resolver.cz/2023-01-26-knot-resolver-5.6.0.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26249.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26249

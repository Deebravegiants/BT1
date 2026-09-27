# [M] Internal logic flaw in cache management can lead to a denial of service in PowerDNS Recursor

## Summary
Severity: Medium
Advisory: CVE-2025-59029
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-59029
Type: osv

## Details
An attacker can trigger an assertion failure by requesting crafted DNS records, waiting for them to be inserted into the records cache, then send a query with qtype set to ANY.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2025-07.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59029.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59029
- https://github.com/PowerDNS/pdns

# [H] CVE-2023-22617

## Summary
Severity: High
Advisory: CVE-2023-22617
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-21
Source: https://osv.dev/vulnerability/CVE-2023-22617
Type: osv

## Details
A remote attacker might be able to cause infinite recursion in PowerDNS Recursor 4.8.0 via a DNS query that retrieves DS records for a misconfigured domain, because QName minimization is used in QM fallback mode. This is fixed in 4.8.1.

## References
- https://docs.powerdns.com/recursor/changelog/4.8.html#change-4.8.1
- https://docs.powerdns.com/recursor/security-advisories/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22617.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22617
- http://www.openwall.com/lists/oss-security/2023/01/20/1

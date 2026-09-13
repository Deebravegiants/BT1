# [H] Crafted responses can lead to a denial of service due to cache inefficiencies in the Recursor

## Summary
Severity: High
Advisory: CVE-2024-25590
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-03
Source: https://osv.dev/vulnerability/CVE-2024-25590
Type: osv

## Details
An attacker can publish a zone containing specific Resource Record Sets.

 Repeatedly processing and caching results for these sets can lead to a 

denial of service.

## References
- http://www.openwall.com/lists/oss-security/2024/10/03/3
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2024-04.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25590.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25590
- https://github.com/PowerDNS/pdns

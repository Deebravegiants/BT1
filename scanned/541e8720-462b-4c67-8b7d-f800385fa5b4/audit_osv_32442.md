# [H] A crafted zone can lead to an illegal memory access in the PowerDNS Recursor

## Summary
Severity: High
Advisory: CVE-2025-30195
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-07
Source: https://osv.dev/vulnerability/CVE-2025-30195
Type: osv

## Details
An attacker can publish a zone containing specific Resource Record Sets. Processing and caching results for these sets can lead to an illegal memory accesses and crash of the Recursor, causing a denial of service.

The remedy is: upgrade to the patched 5.2.1 version.

We would like to thank Volodymyr Ilyin for bringing this issue to our attention.

## References
- http://www.openwall.com/lists/oss-security/2025/04/07/1
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2025-01.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30195.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30195
- https://github.com/PowerDNS/pdns

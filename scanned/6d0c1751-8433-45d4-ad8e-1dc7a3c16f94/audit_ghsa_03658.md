# [H] XML Entity Expansion in Pippo

## Summary
Severity: High
Advisory: GHSA-hwcx-9p4j-7hwj
CVE: CVE-2019-5442
CWE: CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-hwcx-9p4j-7hwj
Type: github-advisory

## Affected
- Maven: `ro.pippo:pippo-jaxb` — affected >=0

## Details
XML Entity Expansion (Billion Laughs Attack) on Pippo 1.12.0 results in Denial of Service.Entities are created recursively and large amounts of heap memory is taken. Eventually, the JVM process will run out of memory. Otherwise, if the OS does not bound the memory on that process, memory will continue to be exhausted and will affect other processes on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5442
- https://hackerone.com/reports/506791

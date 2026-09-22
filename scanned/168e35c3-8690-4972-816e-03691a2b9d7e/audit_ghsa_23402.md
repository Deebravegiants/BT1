# [H] Modoboa is vulnerable to an XML External Entity Injection (XXE)

## Summary
Severity: High
Advisory: GHSA-vc42-mgr2-w34r
CVE: CVE-2019-19702
CWE: CWE-91
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vc42-mgr2-w34r
Type: github-advisory

## Affected
- PyPI: `modoboa-dmarc` — affected >=0 <1.2.0

## Details
The modoboa-dmarc plugin 1.1.0 for Modoboa is vulnerable to an XML External Entity Injection (XXE) attack when processing XML data. A remote attacker could exploit this to perform a denial of service against the DMARC reporting functionality, such as by referencing the /dev/random file within XML documents that are emailed to the address in the rua field of the DMARC records of a domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19702
- https://github.com/modoboa/modoboa-dmarc/issues/38
- https://github.com/modoboa/modoboa-dmarc/commit/14c29e0ad9487bdbe4cc0bd1f8bc711285bf9933
- https://github.com/modoboa/modoboa-dmarc
- https://github.com/pypa/advisory-database/tree/main/vulns/modoboa-dmarc/PYSEC-2019-105.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/modoboa/PYSEC-2019-251.yaml

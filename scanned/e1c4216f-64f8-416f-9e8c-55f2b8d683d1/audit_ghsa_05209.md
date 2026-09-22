# [H] kafka-python vulnerable to denial of service through an unvalidated protocol frame length

## Summary
Severity: High
Advisory: GHSA-m3px-q5gj-j9x7
CVE: CVE-2026-10142
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-m3px-q5gj-j9x7
Type: github-advisory

## Affected
- PyPI: `kafka-python` — affected >=0 <2.3.2

## Details
kafka-python prior to 2.3.2 contains a denial-of-service vulnerability in the protocol parser that allows a malicious broker or machine-in-the-middle attacker to exhaust memory or hang connections by sending a crafted 4-byte frame length value without bounds validation. Attackers can send a specially crafted frame length through the receive_bytes() function to trigger either a multi-gigabyte memory allocation or an uncaught ValueError that leaves the connection in a broken state, causing requests to hang and consumers to stop heartbeating until restart.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10142
- https://github.com/dpkp/kafka-python/pull/3019
- https://github.com/dpkp/kafka-python/pull/3026
- https://github.com/dpkp/kafka-python/commit/6e4831444f972d169cdd11f5c8d50333cea3f19b
- https://github.com/dpkp/kafka-python/commit/9f92d0f53ecfee738c54638867c3d67f83017bca
- https://github.com/dpkp/kafka-python
- https://github.com/dpkp/kafka-python/releases/tag/2.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/kafka-python/PYSEC-2026-2190.yaml
- https://www.vulncheck.com/advisories/kafka-python-prior-to-denial-of-service-via-protocol-parser-frame-length

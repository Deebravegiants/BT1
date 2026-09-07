# [H] websockets is vulnerable to denial of service by memory exhaustion

## Summary
Severity: High
Advisory: GHSA-6g87-ff9q-v847
CVE: CVE-2018-1000518
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-09-17
Source: https://github.com/advisories/GHSA-6g87-ff9q-v847
Type: github-advisory

## Affected
- PyPI: `websockets` — affected >=4.0 <5.0

## Details
The Python websockets library version 4 contains a CWE-409: Improper Handling of Highly Compressed Data (Data Amplification) vulnerability in Servers and clients, unless configured with compression=None that can result in Denial of Service by memory exhaustion. This attack appears to be exploitable via sending a specially crafted frame on an established connection. This vulnerability appears to have been fixed in version 5.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000518
- https://github.com/aaugustin/websockets/pull/407
- https://github.com/aaugustin/websockets
- https://github.com/pypa/advisory-database/tree/main/vulns/websockets/PYSEC-2018-79.yaml

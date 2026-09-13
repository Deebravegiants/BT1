# [M] ml-logger has path traversal in the file argument

## Summary
Severity: Medium
Advisory: GHSA-8x9j-2p8r-7xc6
CVE: CVE-2025-10951
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-8x9j-2p8r-7xc6
Type: github-advisory

## Affected
- PyPI: `ml-logger` — affected >=0

## Details
A vulnerability was identified in geyang ml-logger 0.10.36 and prior. Affected by this vulnerability is the function log_handler of the file ml_logger/server.py. Such manipulation of the argument File leads to path traversal. It is possible to launch the attack remotely. The exploit is publicly available and might be used. This product takes the approach of rolling releases to provide continious delivery. Therefore, version details for affected and updated releases are not available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10951
- https://github.com/geyang/ml-logger/issues/73
- https://github.com/geyang/ml-logger
- https://vuldb.com/?ctiid.325821
- https://vuldb.com/?id.325821
- https://vuldb.com/?submit.652462

# [H] Session Fixation in Tryton

## Summary
Severity: High
Advisory: GHSA-32w7-9whp-cjp9
CVE: CVE-2018-19443
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-29
Source: https://github.com/advisories/GHSA-32w7-9whp-cjp9
Type: github-advisory

## Affected
- PyPI: `tryton` — affected >=5.0.0 <5.0.1

## Details
The client in Tryton 5.x before 5.0.1 tries to make a connection to the bus in cleartext instead of encrypted under certain circumstances in bus.py and jsonrpc.py. This connection attempt fails, but it contains in the header the current session of the user. This session could then be stolen by a man-in-the-middle.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19443
- https://bugs.tryton.org/issue7792
- https://discuss.tryton.org/t/security-release-for-issue7792/830
- https://github.com/pypa/advisory-database/tree/main/vulns/tryton/PYSEC-2018-77.yaml

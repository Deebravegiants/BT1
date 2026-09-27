# [H] Transifex command-line client has improper certificate validation

## Summary
Severity: High
Advisory: GHSA-jf99-2rj4-jxrm
CVE: CVE-2013-7110
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jf99-2rj4-jxrm
Type: github-advisory

## Affected
- PyPI: `transifex-client` — affected >=0 <0.10

## Details
Transifex command-line client before 0.10 does not validate X.509 certificates for data transfer connections, which allows man-in-the-middle attackers to spoof a Transifex server via an arbitrary certificate.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-2073.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7110
- https://github.com/transifex/transifex-client/issues/42
- https://github.com/transifex/transifex-client/commit/e0d1f8b38ec1a24e2999d63420554d8393206f58
- https://github.com/pypa/advisory-database/tree/main/vulns/transifex-client/PYSEC-2014-72.yaml
- https://github.com/transifex/transifex-client
- http://www.openwall.com/lists/oss-security/2013/12/13/5
- http://www.openwall.com/lists/oss-security/2013/12/15/3

# [M] Urllib3 Incorrect Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-v4w5-p2hg-8fh6
CVE: CVE-2016-9015
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v4w5-p2hg-8fh6
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.17 <1.18.1

## Details
Versions 1.17 and 1.18 of the Python urllib3 library suffer from a vulnerability that can cause them, in certain configurations, to not correctly validate TLS certificates. This places users of the library with those configurations at risk of man-in-the-middle and information leakage attacks. This vulnerability affects users using versions 1.17 and 1.18 of the urllib3 library, who are using the optional PyOpenSSL support for TLS instead of the regular standard library TLS backend, and who are using OpenSSL 1.1.0 via PyOpenSSL. This is an extremely uncommon configuration, so the security impact of this vulnerability is low.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9015
- https://github.com/urllib3/urllib3/commit/c32cdbc16a9634fa0f8c829d1270301570158715
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2017-98.yaml
- https://github.com/urllib3/urllib3
- https://web.archive.org/web/20210123184150/http://www.securityfocus.com/bid/93941
- http://www.openwall.com/lists/oss-security/2016/10/27/6

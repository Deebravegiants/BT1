# [H] Pyopenssl Incorrect Memory Management

## Summary
Severity: High
Advisory: GHSA-2rcm-phc9-3945
CVE: CVE-2018-1000808
CWE: CWE-401, CWE-404
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-2rcm-phc9-3945
Type: github-advisory

## Affected
- PyPI: `pyopenssl` — affected >=0 <17.5.0

## Details
It was discovered that pyOpenSSL incorrectly handled memory when performing operations on a PKCS #12 store. A remote attacker could possibly use this issue to cause pyOpenSSL to consume resources, resulting in a denial of service.

This attack appear to be exploitable via Depends upon calling application, however it could be as simple as initiating a TLS connection that would cause the calling application to reload certificates from a PKCS #12 store. This vulnerability appears to have been fixed in 17.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000808
- https://github.com/pyca/pyopenssl/pull/723
- https://github.com/pyca/pyopenssl/commit/e73818600065821d588af475b024f4eb518c3509
- https://access.redhat.com/errata/RHSA-2019:0085
- https://github.com/advisories/GHSA-2rcm-phc9-3945
- https://github.com/pyca/pyopenssl
- https://github.com/pypa/advisory-database/tree/main/vulns/pyopenssl/PYSEC-2018-24.yaml
- https://usn.ubuntu.com/3813-1
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00014.html

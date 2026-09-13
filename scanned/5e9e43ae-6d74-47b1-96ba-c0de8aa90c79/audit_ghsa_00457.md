# [H] PyOpenSSL Use-After-Free vulnerability

## Summary
Severity: High
Advisory: GHSA-p28m-34f6-967q
CVE: CVE-2018-1000807
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-p28m-34f6-967q
Type: github-advisory

## Affected
- PyPI: `pyopenssl` — affected >=0 <17.5.0

## Details
It was discovered that pyOpenSSL incorrectly handled memory when handling X509 objects. A remote attacker could use this issue to cause pyOpenSSL to crash, resulting in a denial of service, or possibly execute arbitrary code. This attack appears to be exploitable via Depends on the calling application and if it retains a reference to the memory. This vulnerability appears to have been fixed in 17.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000807
- https://github.com/pyca/pyopenssl/pull/723
- https://github.com/pyca/pyopenssl/commit/e73818600065821d588af475b024f4eb518c3509
- https://access.redhat.com/errata/RHSA-2019:0085
- https://github.com/pyca/pyopenssl
- https://github.com/pypa/advisory-database/tree/main/vulns/pyopenssl/PYSEC-2018-23.yaml
- https://usn.ubuntu.com/3813-1
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00014.html

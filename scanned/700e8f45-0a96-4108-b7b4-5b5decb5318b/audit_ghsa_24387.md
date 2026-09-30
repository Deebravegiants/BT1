# [M] Apache Libcloud vulnerable to certificate impersonation

## Summary
Severity: Medium
Advisory: GHSA-prcq-52f8-fp44
CVE: CVE-2012-3446
CWE: CWE-185, CWE-20, CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-prcq-52f8-fp44
Type: github-advisory

## Affected
- PyPI: `apache-libcloud` — affected >=0 <0.11.1

## Details
Apache Libcloud before 0.11.1 uses an incorrect regular expression during verification of whether the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via a crafted certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3446
- https://github.com/apache/libcloud/commit/f2af5502dae3ac63e656dd1b7d5f29cc82ded401
- https://github.com/apache/libcloud
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-libcloud/PYSEC-2012-12.yaml
- https://svn.apache.org/repos/asf/libcloud/trunk/CHANGES
- http://www.cs.utexas.edu/~shmat/shmat_ccs12.pdf

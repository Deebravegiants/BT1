# [H] Apache Qpid Python client Improper certificate validation

## Summary
Severity: High
Advisory: GHSA-3g2p-7c6p-vj8c
CVE: CVE-2013-1909
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3g2p-7c6p-vj8c
Type: github-advisory

## Affected
- PyPI: `qpid-python` — affected >=0 <0.22

## Details
The Python client in Apache Qpid before 2.2 does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1909
- https://github.com/apache/qpid-python/commit/7d8f51791c4949404d78f1083f465b7b4c8e954b
- https://github.com/apache/qpid-python
- https://github.com/pypa/advisory-database/tree/main/vulns/qpid-python/PYSEC-2013-25.yaml
- https://issues.apache.org/jira/browse/QPID-4918
- https://web.archive.org/web/20140722191407/http://secunia.com/advisories/53968
- https://web.archive.org/web/20140722194233/http://secunia.com/advisories/54137
- http://qpid.apache.org/releases/qpid-0.22/release-notes.html
- http://rhn.redhat.com/errata/RHSA-2013-1024.html
- http://svn.apache.org/viewvc?view=revision&revision=1460013

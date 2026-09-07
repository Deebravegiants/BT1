# [M] Cleartext Transmission of Sensitive Information in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-v45r-rj5x-hpg2
CVE: CVE-2014-0035
CWE: CWE-319
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v45r-rj5x-hpg2
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <2.6.13
- Maven: `org.apache.cxf:cxf-core` — affected >=2.7.0 <2.7.10

## Details
The SymmetricBinding in Apache CXF before 2.6.13 and 2.7.x before 2.7.10, when EncryptBeforeSigning is enabled and the UsernameToken policy is set to an EncryptedSupportingToken, transmits the UsernameToken in cleartext, which allows remote attackers to obtain sensitive information by sniffing the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0035
- https://github.com/apache/cxf/commit/2d2fd1bf67dc2247b6aca31b83a571d865fad1c9
- https://github.com/apache/cxf/commit/d249721708694cbb0f431c0658166ebdcb02ec15
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2014-0035.txt.asc
- http://rhn.redhat.com/errata/RHSA-2014-0797.html
- http://rhn.redhat.com/errata/RHSA-2014-0798.html
- http://rhn.redhat.com/errata/RHSA-2014-0799.html
- http://rhn.redhat.com/errata/RHSA-2014-1351.html
- http://rhn.redhat.com/errata/RHSA-2015-0850.html
- http://rhn.redhat.com/errata/RHSA-2015-0851.html
- http://svn.apache.org/viewvc?view=revision&revision=1564724

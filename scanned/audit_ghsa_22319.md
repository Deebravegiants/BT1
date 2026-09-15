# [M] Improper Access Control in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-3336-h95j-hvvf
CVE: CVE-2015-5253
CWE: CWE-284
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3336-h95j-hvvf
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-sso-saml` — affected >=0 <2.7.18
- Maven: `org.apache.cxf:cxf-rt-rs-security-sso-saml` — affected >=3.0.0 <3.0.7
- Maven: `org.apache.cxf:cxf-rt-rs-security-sso-saml` — affected >=3.1.0 <3.1.3

## Details
The SAML Web SSO module in Apache CXF before 2.7.18, 3.0.x before 3.0.7, and 3.1.x before 3.1.3 allows remote authenticated users to bypass authentication via a crafted SAML response with a valid signed assertion, related to a "wrapping attack."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5253
- https://github.com/apache/cxf/commit/02245c656941f28b6b2be5e461e6db04a70d2436
- https://github.com/apache/cxf/commit/1c2a53080004d6ce275f2e70f46a0098d4140787
- https://github.com/apache/cxf/commit/845eccb6484b43ba02875c71e824db23ae4f20c0
- https://git-wip-us.apache.org/repos/asf?p=cxf.git;a=commitdiff;h=845eccb6484b43ba02875c71e824db23ae4f20c0
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2015-5253.txt.asc
- http://rhn.redhat.com/errata/RHSA-2016-0321.html
- http://www.openwall.com/lists/oss-security/2015/11/14/1

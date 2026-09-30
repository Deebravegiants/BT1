# [H] Apache CXF Fediz application plugins are vulnerable to Denial of Service (DoS) attacks

## Summary
Severity: High
Advisory: GHSA-3357-829x-m9pr
CVE: CVE-2015-5175
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-3357-829x-m9pr
Type: github-advisory

## Affected
- Maven: `org.apache.cxf.fediz:fediz-idp` — affected >=0 <1.1.3
- Maven: `org.apache.cxf.fediz:fediz-idp` — affected >=1.2 <1.2.1
- Maven: `org.apache.cxf.fediz:fediz-core` — affected >=0 <1.1.3
- Maven: `org.apache.cxf.fediz:fediz-core` — affected >=1.2 <1.2.1

## Details
Application plugins in Apache CXF Fediz prior to version 1.1.3 and 1.2.x prior to 1.2.1 allow remote attackers to create a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5175
- https://github.com/apache/cxf-fediz/commit/f65c961ea31e3c1851daba8e7e49fc37bbf77b19
- https://cxf.apache.org/security-advisories.data/CVE-2015-5175.txt.asc?version=1&modificationDate=1440598018000&api=v2
- https://git-wip-us.apache.org/repos/asf?p=cxf-fediz.git;a=commit;h=f65c961ea31e3c1851daba8e7e49fc37bbf77b19
- https://github.com/advisories/GHSA-3357-829x-m9pr
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- https://mail-archives.apache.org/mod_mbox/cxf-dev/201508.mbox/%3CCAB8XdGAx=VL_uepDSecE2h8ggTD4kpagXnyfegVjt7Axi_Ossw@mail.gmail.com%3E
- http://www.openwall.com/lists/oss-security/2015/08/26/3
- http://www.securityfocus.com/bid/76486

# [H] Apache CXF TLS hostname verification does not work correctly with com.sun.net.ssl.*

## Summary
Severity: High
Advisory: GHSA-jc7r-v6fg-2gpf
CVE: CVE-2018-8039
CWE: CWE-755
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-jc7r-v6fg-2gpf
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-transports-http` — affected >=3.2.0 <3.2.5
- Maven: `org.apache.cxf:cxf-rt-transports-http` — affected >=0 <3.1.16
- Maven: `org.apache.cxf:apache-cxf` — affected >=3.2.0 <3.2.5
- Maven: `org.apache.cxf:apache-cxf` — affected >=0 <3.1.16

## Details
It is possible to configure Apache CXF to use the com.sun.net.ssl implementation via 'System.setProperty("java.protocol.handler.pkgs", "com.sun.net.ssl.internal.www.protocol");'. When this system property is set, CXF uses some reflection to try to make the HostnameVerifier work with the old com.sun.net.ssl.HostnameVerifier interface. However, the default HostnameVerifier implementation in CXF does not implement the method in this interface, and an exception is thrown. However, in Apache CXF prior to 3.2.5 and 3.1.16 the exception is caught in the reflection code and not properly propagated. What this means is that if you are using the com.sun.net.ssl stack with CXF, an error with TLS hostname verification will not be thrown, leaving a CXF client subject to man-in-the-middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8039
- https://github.com/apache/cxf/commit/fae6fabf9bd7647f5e9cb68897a7d72b545b741b
- https://github.com/apache/cxf/commit/8ed6208f987ff72e4c4d2cf8a6b1ec9b27575d4
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/1f8ff31df204ad0374ab26ad333169e0387a5e7ec92422f337431866@%3Cdev.cxf.apache.org%3E
- https://github.com/apache/cxf
- https://github.com/advisories/GHSA-jc7r-v6fg-2gpf
- https://cxf.apache.org/security-advisories.data/CVE-2018-8039.txt.asc
- https://access.redhat.com/errata/RHSA-2018:3817
- https://access.redhat.com/errata/RHSA-2018:3768
- https://access.redhat.com/errata/RHSA-2018:2643
- https://access.redhat.com/errata/RHSA-2018:2428

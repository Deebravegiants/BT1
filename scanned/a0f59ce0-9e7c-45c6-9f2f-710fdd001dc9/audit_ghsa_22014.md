# [M] Improper Certificate Validation in Apache Commons HttpClient

## Summary
Severity: Medium
Advisory: GHSA-3832-9276-x7gf
CVE: CVE-2012-5783
CWE: CWE-295
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3832-9276-x7gf
Type: github-advisory

## Affected
- Maven: `commons-httpclient:commons-httpclient` — affected >=3.0

## Details
Apache Commons HttpClient 3.x, as used in Amazon Flexible Payments Service (FPS) merchant Java SDK and other products, does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

Note that the Commons HttpClient project is [end of life](https://hc.apache.org/httpclient-legacy/). It has been replaced by the Apache HttpComponents project in its [HttpClient](https://hc.apache.org/httpcomponents-client-5.4.x/) and [HttpCore](https://hc.apache.org/httpcomponents-core-5.3.x/) modules. CVE-2012-5783 has been patched in [v4.0](https://repo1.maven.org/maven2/org/apache/httpcomponents/httpclient/4.0/) of the Apache HttpComponents HttpClient module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5783
- https://access.redhat.com/errata/RHSA-2017:0868
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79984
- https://github.com/apache/httpcomponents-client
- https://issues.apache.org/jira/browse/HTTPCLIENT-1265
- http://lists.opensuse.org/opensuse-updates/2013-02/msg00078.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00040.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00041.html
- http://lists.opensuse.org/opensuse-updates/2013-04/msg00053.html
- http://rhn.redhat.com/errata/RHSA-2013-0270.html
- http://rhn.redhat.com/errata/RHSA-2013-0679.html
- http://rhn.redhat.com/errata/RHSA-2013-0680.html
- http://rhn.redhat.com/errata/RHSA-2013-0682.html
- http://rhn.redhat.com/errata/RHSA-2013-1853.html
- http://rhn.redhat.com/errata/RHSA-2014-0224.html
- http://www.cs.utexas.edu/~shmat/shmat_ccs12.pdf
- http://www.ubuntu.com/usn/USN-2769-1

# [M] Authorization Before Parsing and Canonicalization in jetty

## Summary
Severity: Medium
Advisory: GHSA-v7ff-8wcx-gmc5
CVE: CVE-2021-28164
CWE: CWE-200, CWE-551, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-v7ff-8wcx-gmc5
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=9.4.37 <9.4.39

## Details
Release 9.4.37 introduced a more precise implementation of [RFC3986](https://tools.ietf.org/html/rfc3986#section-3.3) with regards to URI decoding, together with some new compliance modes to optionally allow support of some URI that may have ambiguous interpretation within the Servlet specified API methods behaviours.   The default mode allowed % encoded . characters to be excluded for URI normalisation, which is correct by the RFC, but is not assumed by common Servlet implementations. The default compliance mode allows requests with URIs that contain `%2e` or `%2e%2e` segments to access protected resources within the `WEB-INF` directory.  For example a request to `/context/%2e/WEB-INF/web.xml` can retrieve the `web.xml` file.  This can reveal sensitive information regarding the implementation of a web application. Workarounds found by HttpCompliance mode RFC7230_NO_AMBIGUOUS_URIS can be enabled by updating `start.d/http.ini` to include: jetty.http.compliance=RFC7230_NO_AMBIGUOUS_URIS.

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-v7ff-8wcx-gmc5
- https://nvd.nist.gov/vuln/detail/CVE-2021-28164
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://security.netapp.com/advisory/ntap-20210611-0006
- https://lists.apache.org/thread.html/rd7c8fb305a8637480dc943ba08424c8992dccad018cd1405eb2afe0e@%3Cdev.ignite.apache.org%3E
- https://lists.apache.org/thread.html/rd0471252aeb3384c3cfa6d131374646d4641b80dd313e7b476c47a9c@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/rcea249eb7a0d243f21696e4985de33f3780399bf7b31ea1f6d489b8b@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbc075a4ac85e7a8e47420b7383f16ffa0af3b792b8423584735f369f@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/r9974f64723875052e02787b2a5eda689ac5247c71b827d455e5dc9a6@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/r90e7b4c42a96d74c219e448bee6a329ab0cd3205c44b63471d96c3ab@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r8e6c116628c1277c3cf132012a66c46a0863fa2a3037c0707d4640d4@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r7dd079fa0ac6f47ba1ad0af98d7d0276547b8a4e005f034fb1016951@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r780c3c210a05c5bf7b4671303f46afc3fe56758e92864e1a5f0590d0@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r763840320a80e515331cbc1e613fa93f25faf62e991974171a325c82@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r6ac9e263129328c0db9940d72b4a6062e703c58918dd34bd22cdf8dd@%3Cissues.ignite.apache.org%3E
- https://lists.apache.org/thread.html/r5b3693da7ecb8a75c0e930b4ca26a5f97aa0207d9dae4aa8cc65fe6b@%3Cissues.ignite.apache.org%3E
- https://lists.apache.org/thread.html/r4b1fef117bccc7f5fd4c45fd2cabc26838df823fe5ca94bc42a4fd46@%3Cissues.ignite.apache.org%3E
- https://lists.apache.org/thread.html/r4a66bfbf62281e31bc1345ebecbfd96f35199eecd77bfe4e903e906f@%3Cissues.ignite.apache.org%3E

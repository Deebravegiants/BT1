# [M] Ignite Realtime Openfire allows remote authenticated users to cause a denial of service

## Summary
Severity: Medium
Advisory: GHSA-x337-43mr-gg3h
CVE: CVE-2008-1728
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-x337-43mr-gg3h
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:parent` — affected >=0 <3.5.0
- Maven: `org.igniterealtime.openfire:openfire` — affected >=0 <3.5.0

## Details
ConnectionManagerImpl.java in Ignite Realtime Openfire 3.4.5 allows remote authenticated users to cause a denial of service (daemon outage) by triggering large outgoing queues without reading messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1728
- https://github.com/igniterealtime/Openfire/commit/c9cd1e521673ef0cccb8795b78d3cbaefb8a576a
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41744
- https://github.com/igniterealtime/Openfire
- https://web.archive.org/web/20080517012408/http://www.securityfocus.com/bid/28722
- https://web.archive.org/web/20080628231441/http://secunia.com/advisories/29751
- https://web.archive.org/web/20080724051528/http://secunia.com/advisories/29901
- http://security.gentoo.org/glsa/glsa-200804-26.xml
- http://www.igniterealtime.org/builds/openfire/docs/latest/changelog.html
- http://www.igniterealtime.org/fisheye/changelog/svn-org?cs=10031
- http://www.igniterealtime.org/issues/browse/JM-1289
- http://www.openwall.com/lists/oss-security/2008/04/10/7

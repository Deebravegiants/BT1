# [H] Ignite Realtime Openfire vulnerable to XMPPbomb attack

## Summary
Severity: High
Advisory: GHSA-j5qh-cp3p-2h87
CVE: CVE-2014-2741
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j5qh-cp3p-2h87
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:parent` — affected >=0 <3.9.2

## Details
nio/XMLLightweightParser.java in Ignite Realtime Openfire before 3.9.2 does not properly restrict the processing of compressed XML elements, which allows remote attackers to cause a denial of service (resource consumption) via a crafted XMPP stream, aka an "xmppbomb" attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2741
- https://github.com/igniterealtime/Openfire/commit/3aec383e07ee893b77396fe946766bbd3758af77
- https://github.com/igniterealtime/Openfire
- https://web.archive.org/web/20140407092132/http://xmpp.org/resources/security-notices/uncontrolled-resource-consumption-with-highly-compressed-xmpp-stanzas
- https://web.archive.org/web/20140705161237/http://fisheye.igniterealtime.org/changelog/openfiregit?cs=3aec383e07ee893b77396fe946766bbd3758af77
- http://community.igniterealtime.org/thread/52317
- http://openwall.com/lists/oss-security/2014/04/07/7
- http://openwall.com/lists/oss-security/2014/04/09/1
- http://www.kb.cert.org/vuls/id/495476

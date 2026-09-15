# [H] Jetty vulnerable to exposure of sensitive information to unauthenticated remote users

## Summary
Severity: High
Advisory: GHSA-ghgj-3xqr-6jfm
CVE: CVE-2015-2080
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-ghgj-3xqr-6jfm
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <9.2.9.v20150224

## Details
The exception handling code in Eclipse Jetty prior to 9.2.9.v20150224 allows remote attackers to obtain sensitive information from process memory via illegal characters in an HTTP header, aka JetLeak.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2080
- https://blog.gdssecurity.com/labs/2015/2/25/jetleak-vulnerability-remote-leakage-of-shared-buffers-in-je.html
- https://github.com/advisories/GHSA-ghgj-3xqr-6jfm
- https://github.com/eclipse/jetty.project/blob/jetty-9.2.x/advisories/2015-02-24-httpparser-error-buffer-bleed.md
- https://security.netapp.com/advisory/ntap-20190307-0005
- http://dev.eclipse.org/mhonarc/lists/jetty-announce/msg00074.html
- http://dev.eclipse.org/mhonarc/lists/jetty-announce/msg00075.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/151804.html
- http://packetstormsecurity.com/files/130567/Jetty-9.2.8-Shared-Buffer-Leakage.html
- http://seclists.org/fulldisclosure/2015/Mar/12
- http://www.securityfocus.com/archive/1/534755/100/1600/threaded
- http://www.securityfocus.com/bid/72768
- http://www.securitytracker.com/id/1031800

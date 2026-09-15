# [C] Insecure Deserialization in Apache XML-RPC

## Summary
Severity: Critical
Advisory: GHSA-6vwp-35w3-xph8
CVE: CVE-2019-17570
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-6vwp-35w3-xph8
Type: github-advisory

## Affected
- Maven: `org.apache.xmlrpc:xmlrpc` — affected >=0

## Details
An untrusted deserialization was found in the org.apache.xmlrpc.parser.XmlRpcResponseParser:addResult method of Apache XML-RPC (aka ws-xmlrpc) library. A malicious XML-RPC server could target a XML-RPC client causing it to execute arbitrary code.

Apache XML-RPC is no longer maintained and this issue will not be fixed.

## References
- https://github.com/orangecertcc/security-research/security/advisories/GHSA-x2r6-4m45-m4jp
- https://nvd.nist.gov/vuln/detail/CVE-2019-17570
- https://access.redhat.com/errata/RHSA-2020:0310
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-17570%3B
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-17570;
- https://lists.apache.org/thread.html/846551673bbb7ec8d691008215384bcef03a3fb004d2da845cfe88ee%401390230951%40%3Cdev.ws.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/01/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I3QCRLJYQRGVTIYF4BXYRFSF3ONP3TBF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I3QCRLJYQRGVTIYF4BXYRFSF3ONP3TBF
- https://seclists.org/bugtraq/2020/Feb/8
- https://security.gentoo.org/glsa/202401-26
- https://usn.ubuntu.com/4496-1
- https://www.debian.org/security/2020/dsa-4619
- http://www.openwall.com/lists/oss-security/2020/01/24/2

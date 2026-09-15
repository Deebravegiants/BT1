# [H] HTTP response splitting in CGI

## Summary
Severity: High
Advisory: GHSA-vc47-6rqg-c7f5
CVE: CVE-2021-33621
CWE: CWE-436, CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-19
Source: https://github.com/advisories/GHSA-vc47-6rqg-c7f5
Type: github-advisory

## Affected
- RubyGems: `cgi` — affected >=0.3.0 <0.3.5
- RubyGems: `cgi` — affected >=0.2.0 <0.2.2
- RubyGems: `cgi` — affected >=0 <0.1.0.2

## Details
Ruby gem cgi.rb prior to versions 0.3.5, 0.2.2 and 0.1.0.2 allow HTTP header injection. If a CGI application using the CGI library inserts untrusted input into the HTTP response header, an attacker can exploit it to insert a newline character to split a header, and inject malicious content to deceive clients. This issue has been patched in versions 0.3.5, 0.2.2 and 0.1.0.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33621
- https://hackerone.com/reports/1204695
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cgi/CVE-2021-33621.yml
- https://lists.debian.org/debian-lts-announce/2023/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DQR7LWED6VAPD5ATYOBZIGJQPCUBRJBX
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/THVTYHHEOVLQFCFHWURZYO7PVUPBHRZD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YACE6ORF2QBXXBK2V2CM36D7TZMEJVAS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DQR7LWED6VAPD5ATYOBZIGJQPCUBRJBX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/THVTYHHEOVLQFCFHWURZYO7PVUPBHRZD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YACE6ORF2QBXXBK2V2CM36D7TZMEJVAS
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20221228-0004
- https://www.ruby-lang.org/en/news/2022/11/22/http-response-splitting-in-cgi-cve-2021-33621

# [H] Nokogiri contains libxml Out-of-bounds Write vulnerability

## Summary
Severity: High
Advisory: GHSA-jw9f-hh49-cvp9
CVE: CVE-2021-3517
CWE: CWE-787
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jw9f-hh49-cvp9
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.11.4

## Details
There is a flaw in the xml entity encoding functionality of libxml2 in versions before 2.9.11. An attacker who is able to supply a crafted file to be processed by an application linked with the affected functionality of libxml2 could trigger an out-of-bounds read. The most likely impact of this flaw is to application availability, with some potential impact to confidentiality and integrity if an attacker is able to use memory information to further exploit the application.

Nokogiri prior to version 1.11.4 used a vulnerable version of libxml2. Nokogiri 1.11.4 updated libxml2 to version 2.9.11 to address this and other vulnerabilities in libxml2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3517
- https://github.com/sparklemotion/nokogiri/issues/2233
- https://github.com/sparklemotion/nokogiri/issues/2274
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://security.netapp.com/advisory/ntap-20211022-0004
- https://security.netapp.com/advisory/ntap-20210625-0002
- https://security.gentoo.org/glsa/202107-05
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVM4UJ3376I6ZVOYMHBNX4GY3NIV52WV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BZOMV5J4PMZAORVT64BKLV6YIZAFDGX6
- https://lists.debian.org/debian-lts-announce/2021/05/msg00008.html
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/8598060bacada41a0eb09d95c97744ff4e428f8e
- https://github.com/sparklemotion/nokogiri/blob/7c19ef5cc6b7c5c36827dd5495f857c6877ec8cf/CHANGELOG.md?plain=1#L579
- https://github.com/sparklemotion/nokogiri
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2021-3517.yml
- https://bugzilla.redhat.com/show_bug.cgi?id=1954232

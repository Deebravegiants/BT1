# [M] Nokogiri Implements libxml2 version vulnerable to null pointer dereferencing

## Summary
Severity: Medium
Advisory: GHSA-286v-pcf5-25rc
CVE: CVE-2021-3537
CWE: CWE-476
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-286v-pcf5-25rc
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.11.4

## Details
A vulnerability found in libxml2 in versions before 2.9.11 shows that it did not propagate errors while parsing XML mixed content, causing a NULL dereference. If an untrusted XML document was parsed in recovery mode and post-validated, the flaw could be used to crash the application. The highest threat from this vulnerability is to system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3537
- https://bugzilla.redhat.com/show_bug.cgi?id=1956522
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2021-3537.yml
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/blob/2edbbef95f1dc12c1ddc5ebda71b9159026245fe/CHANGELOG.md?plain=1#L722
- https://lists.debian.org/debian-lts-announce/2021/05/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BZOMV5J4PMZAORVT64BKLV6YIZAFDGX6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVM4UJ3376I6ZVOYMHBNX4GY3NIV52WV
- https://nokogiri.org/CHANGELOG.html#1114-2021-05-14
- https://security.gentoo.org/glsa/202107-05
- https://security.netapp.com/advisory/ntap-20210625-0002
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html

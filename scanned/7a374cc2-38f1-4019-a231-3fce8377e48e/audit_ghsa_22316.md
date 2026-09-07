# [H] Nokogiri Implements libxml2 version vulnerable to use-after-free

## Summary
Severity: High
Advisory: GHSA-v4f8-2847-rwm7
CVE: CVE-2021-3518
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v4f8-2847-rwm7
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.11.4

## Details
There's a flaw in libxml2 in versions before 2.9.11. An attacker who is able to submit a crafted file to be processed by an application linked with libxml2 could trigger a use-after-free. The greatest impact from this flaw is to confidentiality, integrity, and availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3518
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://support.apple.com/kb/HT212605
- https://support.apple.com/kb/HT212604
- https://support.apple.com/kb/HT212602
- https://support.apple.com/kb/HT212601
- https://security.netapp.com/advisory/ntap-20210625-0002
- https://security.gentoo.org/glsa/202107-05
- https://nokogiri.org/CHANGELOG.html#1114-2021-05-14
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVM4UJ3376I6ZVOYMHBNX4GY3NIV52WV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BZOMV5J4PMZAORVT64BKLV6YIZAFDGX6
- https://lists.debian.org/debian-lts-announce/2021/05/msg00008.html
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b@%3Cissues.bookkeeper.apache.org%3E
- https://github.com/sparklemotion/nokogiri/blob/2edbbef95f1dc12c1ddc5ebda71b9159026245fe/CHANGELOG.md?plain=1#L722
- https://github.com/sparklemotion/nokogiri
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2021-3518.yml
- https://bugzilla.redhat.com/show_bug.cgi?id=1954242

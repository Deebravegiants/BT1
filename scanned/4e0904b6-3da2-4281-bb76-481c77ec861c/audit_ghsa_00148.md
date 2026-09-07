# [H] Denial of service or RCE from libxml2 and libxslt

## Summary
Severity: High
Advisory: GHSA-7hp2-xwpj-95jq
CVE: CVE-2015-8806
CWE: CWE-125
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-09-17
Source: https://github.com/advisories/GHSA-7hp2-xwpj-95jq
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.6.0 <1.6.8

## Details
Nokogiri is affected by series of vulnerabilities in libxml2 and libxslt, which are libraries Nokogiri depends on. It was discovered that libxml2 and libxslt incorrectly handled certain malformed documents, which can allow malicious users to cause issues ranging from denial of service to remote code execution attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8806
- https://github.com/sparklemotion/nokogiri/issues/1473
- https://bugzilla.gnome.org/show_bug.cgi?id=749115
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2015-8806.yml
- https://github.com/sparklemotion/nokogiri
- https://security.gentoo.org/glsa/201701-37
- https://web.archive.org/web/20160928171015/http://www.securityfocus.com/bid/82071
- https://www.debian.org/security/2016/dsa-3593
- http://www.openwall.com/lists/oss-security/2016/02/03/5
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.ubuntu.com/usn/USN-2994-1

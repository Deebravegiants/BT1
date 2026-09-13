# [M] Uncontrolled resource consumption in nokogiri

## Summary
Severity: Medium
Advisory: GHSA-882p-jqgm-f45g
CVE: CVE-2017-18258
CWE: CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-04-13
Source: https://github.com/advisories/GHSA-882p-jqgm-f45g
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.8.2

## Details
The xz_head function in xzlib.c in libxml2 before 2.9.6 allows remote attackers to cause a denial of service (memory consumption) via a crafted LZMA file, because the decoder functionality does not restrict memory usage to what is required for a legitimate file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18258
- https://git.gnome.org/browse/libxml2/commit/?id=e2a9122b8dde53d320750451e9907a7dcb2ca8bb
- https://github.com/advisories/GHSA-882p-jqgm-f45g
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2017-18258.yml
- https://kc.mcafee.com/corporate/index?page=content&id=SB10284
- https://lists.debian.org/debian-lts-announce/2018/09/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00009.html
- https://security.netapp.com/advisory/ntap-20190719-0001
- https://usn.ubuntu.com/3739-1

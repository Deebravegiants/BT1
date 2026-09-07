# [C] Nokogiri vulnerable to libxslt protection mechanism bypass

## Summary
Severity: Critical
Advisory: GHSA-qxcg-xjjg-66mj
CVE: CVE-2019-11068
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qxcg-xjjg-66mj
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.10.3

## Details
A dependency of Nokogiri, libxslt through 1.1.33 allows bypass of a protection mechanism because callers of `xsltCheckRead` and `xsltCheckWrite` permit access even upon receiving a `-1` error code. `xsltCheckRead` can return `-1` for a crafted URL that is not actually invalid and is subsequently loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11068
- https://github.com/sparklemotion/nokogiri/issues/1892
- https://github.com/sparklemotion/nokogiri/pull/1898
- https://github.com/sparklemotion/nokogiri/commit/fe034aedcc59b566740567d621843731686676b9
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://usn.ubuntu.com/3947-2
- https://usn.ubuntu.com/3947-1
- https://security.netapp.com/advisory/ntap-20191017-0001
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SK4YNISS22MJY22YX5I6V2U63QZAUEHA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCOAX2IHUMKCM3ILHTMGLHCDSBTLP2JU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/36TEYN37XCCKN2XUMRTBBW67BPNMSW4K
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SK4YNISS22MJY22YX5I6V2U63QZAUEHA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GCOAX2IHUMKCM3ILHTMGLHCDSBTLP2JU
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36TEYN37XCCKN2XUMRTBBW67BPNMSW4K
- https://lists.debian.org/debian-lts-announce/2019/04/msg00016.html
- https://gitlab.gnome.org/GNOME/libxslt/commit/e03553605b45c88f0b4b2980adfbbb8f6fca2fd6
- https://github.com/sparklemotion/nokogiri/blob/f7aa3b0b29d6fe5fafe93dacd9b96b6b3d16b7ec/CHANGELOG.md?plain=1#L826
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2019-11068.yml
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00052.html

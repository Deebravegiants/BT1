# [H] libxml as used in Nokogiri has an infinite loop in a certain end-of-file situation

## Summary
Severity: High
Advisory: GHSA-7553-jr98-vx47
CVE: CVE-2020-7595
CWE: CWE-835
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-02-24
Source: https://github.com/advisories/GHSA-7553-jr98-vx47
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.10.8

## Details
xmlStringLenDecodeEntities in parser.c in libxml2 2.9.10 has an infinite loop in a certain end-of-file situation.
The Nokogiri RubyGem has patched its vendored copy of libxml2 in order to prevent this issue from affecting nokogiri.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7595
- https://github.com/sparklemotion/nokogiri/issues/1992
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://usn.ubuntu.com/4274-1
- https://us-cert.cisa.gov/ics/advisories/icsa-21-103-08
- https://security.netapp.com/advisory/ntap-20200702-0005
- https://security.gentoo.org/glsa/202010-04
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JDPF3AAVKUAKDYFMFKSIQSVVS3EEFPQH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5R55ZR52RMBX24TQTWHCIWKJVRV6YAWI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/545SPOI3ZPPNPX4TFRIVE4JVRTJRKULL
- https://lists.debian.org/debian-lts-announce/2020/09/msg00009.html
- https://gitlab.gnome.org/GNOME/libxml2/commit/0e1a49c89076
- https://github.com/sparklemotion/nokogiri
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2020-7595.yml
- https://cert-portal.siemens.com/productcert/pdf/ssa-292794.pdf
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00047.html

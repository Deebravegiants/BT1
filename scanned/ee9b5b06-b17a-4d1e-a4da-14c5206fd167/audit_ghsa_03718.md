# [H] Nokogiri NULL Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-6qvp-r6r3-9p7h
CVE: CVE-2018-14404
CWE: CWE-476
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-01-17
Source: https://github.com/advisories/GHSA-6qvp-r6r3-9p7h
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.8.5

## Details
A NULL pointer dereference vulnerability exists in the `xpath.c:xmlXPathCompOpEval()` function of libxml2 through 2.9.8 when parsing an invalid XPath expression in the `XPATH_OP_AND` or `XPATH_OP_OR` case. Applications processing untrusted XSL format inputs with the use of the libxml2 library may be vulnerable to a denial of service attack due to a crash of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14404
- https://github.com/sparklemotion/nokogiri/issues/1785
- https://access.redhat.com/errata/RHSA-2019:1543
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=901817
- https://bugzilla.redhat.com/show_bug.cgi?id=1595985
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2018-14404.yml
- https://gitlab.gnome.org/GNOME/libxml2/issues/10
- https://lists.debian.org/debian-lts-announce/2018/09/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00009.html
- https://security.netapp.com/advisory/ntap-20190719-0002
- https://usn.ubuntu.com/3739-1
- https://usn.ubuntu.com/3739-2

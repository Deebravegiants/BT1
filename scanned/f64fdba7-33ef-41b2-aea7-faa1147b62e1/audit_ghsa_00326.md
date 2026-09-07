# [H] Nokogiri implementation of libxslt lacks integer overflow checks

## Summary
Severity: High
Advisory: GHSA-pf6m-fxpq-fg8v
CVE: CVE-2017-5029
CWE: CWE-787
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-pf6m-fxpq-fg8v
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.7.2

## Details
The xsltAddTextString function in transform.c in libxslt 1.1.29, as used in Nokogiri prior to 1.7.2, lacked a check for integer overflow during a size calculation, which allowed a remote attacker to perform an out of bounds memory write via a crafted HTML page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5029
- https://github.com/sparklemotion/nokogiri/issues/1634
- https://git.gnome.org/browse/libxslt/commit/?id=08ab2774b870de1c7b5a48693df75e8154addae5
- https://github.com/advisories/GHSA-pf6m-fxpq-fg8v
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2017-5029.yml
- https://github.com/sparklemotion/nokogiri
- https://ubuntu.com/security/CVE-2017-5029
- https://ubuntu.com/security/notices/USN-3271-1

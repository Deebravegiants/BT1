# [H] Nokogiri Inefficient Regular Expression Complexity

## Summary
Severity: High
Advisory: GHSA-crjr-9rc5-ghw8
CVE: CVE-2022-24836
CWE: CWE-1333, CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-11
Source: https://github.com/advisories/GHSA-crjr-9rc5-ghw8
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.13.4

## Details
## Summary

Nokogiri `< v1.13.4` contains an inefficient regular expression that is susceptible to excessive backtracking when attempting to detect encoding in HTML documents.

## Mitigation

Upgrade to Nokogiri `>= 1.13.4`.


## Severity

The Nokogiri maintainers have evaluated this as [**High Severity** 7.5 (CVSS3.1)](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H).


## References

[CWE-1333](https://cwe.mitre.org/data/definitions/1333.html) Inefficient Regular Expression Complexity


## Credit

This vulnerability was reported by HackerOne user ooooooo_q (ななおく).

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-crjr-9rc5-ghw8
- https://nvd.nist.gov/vuln/detail/CVE-2022-24836
- https://github.com/sparklemotion/nokogiri/commit/e444525ef1634b675cd1cf52d39f4320ef0aecfd
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2022-24836.yml
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/releases/tag/v1.13.4
- https://groups.google.com/g/ruby-security-ann/c/vX7qSjsvWis/m/TJWN4oOKBwAJ?utm_medium=email&utm_source=footer
- https://lists.debian.org/debian-lts-announce/2022/05/msg00013.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6DHCOWMA5PQTIQIMDENA7R2Y5BDYAIYM
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OUPLBUZVM4WPFSXBEP2JS3R6LMKRTLFC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XMDCWRQXJQ3TFSETPCEFMQ6RR6ME5UA3
- https://security.gentoo.org/glsa/202208-29
- https://support.apple.com/kb/HT213532
- http://seclists.org/fulldisclosure/2022/Dec/23

# [H] Inline DTD allows XML bomb attack

## Summary
Severity: High
Advisory: GHSA-qpmc-wprv-x746
CVE: CVE-2019-15160
CWE: CWE-611, CWE-776
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-qpmc-wprv-x746
Type: github-advisory

## Affected
- Hex: `sweet_xml` — affected >=0 <0.7.0

## Details
The SweetXml (aka sweet_xml) package through 0.6.6 for Erlang and Elixir allows attackers to cause a denial of service (resource consumption) via an XML entity expansion attack with an inline DTD.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15160
- https://github.com/kbrw/sweet_xml/issues/71
- https://github.com/kbrw/sweet_xml
- https://hex.pm/packages/sweet_xml

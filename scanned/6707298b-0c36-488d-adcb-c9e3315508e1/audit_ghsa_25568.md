# [H] Denial of service in HtmlUnit-Neko

## Summary
Severity: High
Advisory: GHSA-g9hh-vvx3-v37v
CVE: CVE-2022-28366
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-g9hh-vvx3-v37v
Type: github-advisory

## Affected
- Maven: `net.sourceforge.htmlunit:neko-htmlunit` — affected >=0 <2.27

## Details
Certain Neko-related HTML parsers allow a denial of service via crafted Processing Instruction (PI) input that causes excessive heap memory consumption. In particular, this issue exists in HtmlUnit-Neko through 2.26, and is fixed in 2.27. This issue also exists in CyberNeko HTML through 1.9.22 (also affecting OWASP AntiSamy before 1.6.6), but 1.9.22 is the last version of CyberNeko HTML. NOTE: this may be related to CVE-2022-24939.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28366
- https://github.com/HtmlUnit/htmlunit-neko
- https://github.com/nahsra/antisamy/releases/tag/v1.6.6
- https://search.maven.org/artifact/net.sourceforge.htmlunit/neko-htmlunit
- https://sourceforge.net/projects/htmlunit/files/htmlunit/2.27

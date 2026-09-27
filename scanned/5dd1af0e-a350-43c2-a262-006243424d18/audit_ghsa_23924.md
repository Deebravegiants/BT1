# [H] libxslt Type Confusion vulnerability that affects Nokogiri

## Summary
Severity: High
Advisory: GHSA-cf46-6xxh-pc75
CVE: CVE-2019-13118
CWE: CWE-843
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cf46-6xxh-pc75
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.10.5

## Details
In `numbers.c` in libxslt 1.1.33, a type holding grouping characters of an `xsl:number` instruction was too narrow and an invalid character/length combination could be passed to `xsltNumberFormatDecimal`, leading to a read of uninitialized stack data.

Nokogiri prior to version 1.10.5 used a vulnerable version of libxslt. Nokogiri 1.10.5 updated libxslt to version 1.1.34 to address this and other vulnerabilities in libxslt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13118
- https://github.com/sparklemotion/nokogiri/issues/1943
- https://github.com/sparklemotion/nokogiri/commit/43a175339b47b8c604508813fc75b83f13cd173e
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15069
- https://seclists.org/bugtraq/2019/Jul/36
- https://seclists.org/bugtraq/2019/Jul/37
- https://seclists.org/bugtraq/2019/Jul/40
- https://seclists.org/bugtraq/2019/Jul/41
- https://seclists.org/bugtraq/2019/Jul/42
- https://security.netapp.com/advisory/ntap-20190806-0004
- https://security.netapp.com/advisory/ntap-20200122-0003
- https://support.apple.com/kb/HT210346
- https://support.apple.com/kb/HT210348
- https://support.apple.com/kb/HT210351
- https://support.apple.com/kb/HT210353
- https://support.apple.com/kb/HT210356
- https://support.apple.com/kb/HT210357
- https://support.apple.com/kb/HT210358
- https://usn.ubuntu.com/4164-1
- https://www.oracle.com/security-alerts/cpujan2020.html

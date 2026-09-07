# [H] Uncontrolled recursion in trust-dns-proto

## Summary
Severity: High
Advisory: GHSA-369h-pjr2-6wrh
CVE: CVE-2018-20994
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-369h-pjr2-6wrh
Type: github-advisory

## Affected
- crates.io: `trust-dns-proto` — affected >=0 <0.4.3

## Details
There's a stack overflow leading to a crash when Trust-DNS's parses a malicious DNS packet. Affected versions of this crate did not properly handle parsing of DNS message compression (RFC1035 section 4.1.4). The parser could be tricked into infinite loop when a compression offset pointed back to the same domain name to be parsed. This allows an attacker to craft a malicious DNS packet which when consumed with Trust-DNS could cause stack overflow and crash the affected software.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20994
- https://github.com/bluejekyll/trust-dns
- https://rustsec.org/advisories/RUSTSEC-2018-0007.html

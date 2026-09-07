# [H] teampass vulnerable to code injection

## Summary
Severity: High
Advisory: GHSA-prj5-2g2p-x2mw
CVE: CVE-2023-2591
CWE: CWE-79, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-05-09
Source: https://github.com/advisories/GHSA-prj5-2g2p-x2mw
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <3.0.7

## Details
In nilsteampassnet/teampass prior to 3.0.7, if two users have the same folder access, malicious users can create an item where its label field is vulnerable to HTML injection. When other users see that item, it may force them to redirect to the attacker's website or capture their data using a form. The issue is fixed in version 3.0.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2591
- https://github.com/nilsteampassnet/teampass/commit/57a977c6323656e5dc06ab5c227e75c3465a1a4a
- https://github.com/nilsteampassnet/TeamPass
- https://huntr.dev/bounties/705f79f4-f5e3-41d7-82a5-f00441cd984b

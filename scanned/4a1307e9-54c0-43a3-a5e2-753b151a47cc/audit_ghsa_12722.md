# [H] Luxon Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: High
Advisory: GHSA-3xq5-wjfh-ppjc
CVE: CVE-2023-22467
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-3xq5-wjfh-ppjc
Type: github-advisory

## Affected
- npm: `luxon` — affected >=1.0.0 <1.28.1
- npm: `luxon` — affected >=2.0.0 <2.5.2
- npm: `luxon` — affected >=3.0.0 <3.2.1

## Details
# Impact
Luxon's `DateTime.fromRFC2822() has quadratic (N^2) complexity on some specific inputs. This causes a noticeable slowdown for inputs with lengths above 10k characters. Users providing untrusted data to this method are therefore vulnerable to (Re)DoS attacks.

This is the same bug as Moment's https://github.com/moment/moment/security/advisories/GHSA-wc69-rhjr-hc9g

# Workarounds
Limit the length of the input.

# References
There is an excellent writeup of the same issue in Moment: https://github.com/moment/moment/pull/6015#issuecomment-1152961973

# Details
`DateTime.fromRFC2822("(".repeat(500000))` takes a couple minutes to complete.

## References
- https://github.com/moment/luxon/security/advisories/GHSA-3xq5-wjfh-ppjc
- https://github.com/moment/moment/security/advisories/GHSA-wc69-rhjr-hc9g
- https://nvd.nist.gov/vuln/detail/CVE-2023-22467
- https://github.com/moment/moment/pull/6015#issuecomment-1152961973
- https://github.com/moment/luxon/commit/5ab3bf64a10da929a437629cdb2f059bb83212bf
- https://github.com/moment/luxon
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/44I3WAJKYXDLOVYRGMHAUXMIV4SPFXDZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4LIVOASKBQH7FEUI5RWM3SOHR6VK7ZZR

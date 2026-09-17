# [H] Sub2API Vulnerable to Password Reset Poisoning via Host Header Trust Issue, Leading to Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-27812
Aliases: GHSA-vc2q-289v-74g3
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27812
Type: osv

## Details
Sub2API is an AI API gateway platform designed to distribute and manage API quotas from AI product subscriptions. A vulnerability in versions prior to 0.1.85 is a Password Reset Poisoning (Host Header / Forwarded Header trust issue), which allows attackers to manipulate the password reset link. Attackers can exploit this flaw to inject their own domain into the password reset link, leading to the potential for account takeover. The vulnerability has been fixed in version v0.1.85. If upgrading is not immediately possible, users can mitigate the vulnerability by disabling the "forgot password" feature until an upgrade to a patched version can be performed. This will prevent attackers from exploiting the vulnerability via the affected endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27812.json
- https://github.com/Wei-Shaw/sub2api/security/advisories/GHSA-vc2q-289v-74g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-27812

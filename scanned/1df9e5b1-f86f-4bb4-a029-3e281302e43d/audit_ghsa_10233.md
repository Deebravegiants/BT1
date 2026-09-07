# [C] parisneo/lollms vulnerable to stored XSS in the social feature

## Summary
Severity: Critical
Advisory: GHSA-8wrq-fv5f-pfp2
CVE: CVE-2026-1115
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8wrq-fv5f-pfp2
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0 <2.2.0

## Details
A Stored Cross-Site Scripting (XSS) vulnerability was identified in the social feature of parisneo/lollms, affecting the latest version prior to 2.2.0. The vulnerability exists in the `create_post` function within `backend/routers/social/__init__.py`, where user-provided content is directly assigned to the `DBPost` model without sanitization. This allows attackers to inject and store malicious JavaScript, which is executed in the browsers of users viewing the Home Feed, including administrators. This can lead to account takeover, session hijacking, and wormable attacks. The issue is resolved in version 2.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1115
- https://github.com/parisneo/lollms/commit/9767b882dbc893c388a286856beeaead69b8292a
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/099aa4fe-7165-4337-889c-3fb4f1aa71aa

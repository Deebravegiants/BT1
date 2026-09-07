# [M] Cross-site Scripting in livehelperchat

## Summary
Severity: Medium
Advisory: GHSA-8wcc-f2vq-h4gx
CVE: CVE-2022-0370
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-8wcc-f2vq-h4gx
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.93

## Details
Stored XSS is found in Settings>Live help configuration>Personal Theme>static content. Under the NAME field put a payload {{constructor.constructor('alert(1)')()}} while creating content, and you will see that the input gets stored, and every time the user visits, the payload gets executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0370
- https://github.com/livehelperchat/livehelperchat/commit/9f5bc33c943349bd765b991db0b7f6b6ef05cfdb
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/fbe4b376-57ce-42cd-a9a9-049c4099b3ca

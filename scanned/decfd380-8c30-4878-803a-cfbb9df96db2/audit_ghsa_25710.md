# [M] An attacker can execute malicious javascript in Live Helper Chat

## Summary
Severity: Medium
Advisory: GHSA-9hgc-wpc5-v8p9
CVE: CVE-2022-1530
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-9hgc-wpc5-v8p9
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.99

## Details
Cross-site Scripting (XSS) in GitHub repository livehelperchat/livehelperchat prior to 3.99v. Attacker can execute malicious javascript on application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1530
- https://github.com/livehelperchat/livehelperchat/commit/edef7a8387be718d0de2dfd1e722789afb0461bc
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/8fd8de01-7e83-4324-9cc8-a97acb9b70d6

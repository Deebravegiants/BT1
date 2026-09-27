# [H] CVE-2025-30066

## Summary
Severity: High
Advisory: CVE-2025-30066
Aliases: GHSA-mrrh-fwg8-r2c3
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-03-15
Source: https://osv.dev/vulnerability/CVE-2025-30066
Type: osv

## Details
tj-actions changed-files before 46 allows remote attackers to discover secrets by reading actions logs. (The tags v1 through v45.0.7 were affected on 2025-03-14 and 2025-03-15 because they were modified by a threat actor to point at commit 0e58ed8, which contained malicious updateFeatures code.)

## References
- https://github.com/github/docs/blob/962a1c8dccb8c0f66548b324e5b921b5e4fbc3d6/content/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions.md?plain=1#L191-L193
- https://github.com/tj-actions/changed-files/blob/45fb12d7a8bedb4da42342e52fe054c6c2c3fd73/README.md?plain=1#L20-L28
- https://news.ycombinator.com/item?id=43367987
- https://news.ycombinator.com/item?id=43368870
- https://web.archive.org/web/20250315060250/https://github.com/tj-actions/changed-files/issues/2463
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-30066
- https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-github-action-cve-2025-30066
- https://www.stream.security/post/github-action-supply-chain-attack-exposes-secrets-what-you-need-to-know-and-how-to-respond
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30066.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30066
- https://github.com/espressif/arduino-esp32/issues/11127
- https://github.com/modal-labs/modal-examples/issues/1100
- https://github.com/tj-actions/changed-files/issues/2463
- https://github.com/tj-actions/changed-files/issues/2464
- https://github.com/tj-actions/changed-files/issues/2477
- https://github.com/chains-project/maven-lockfile/pull/1111
- https://github.com/rackerlabs/genestack/pull/903
- https://blog.gitguardian.com/compromised-tj-actions/
- https://semgrep.dev/blog/2025/popular-github-action-tj-actionschanged-files-is-compromised/
- https://sysdig.com/blog/detecting-and-mitigating-the-tj-actions-changed-files-supply-chain-attack-cve-2025-30066/

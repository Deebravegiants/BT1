# [H] Arbitrary command injection in embano1/wip 

## Summary
Severity: High
Advisory: GHSA-rg3q-prf8-qxmp
CVE: CVE-2023-30623
CWE: CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-rg3q-prf8-qxmp
Type: github-advisory

## Affected
- GitHub Actions: `embano1/wip` — affected >=0 <2

## Details
## Summary
The  `embano1/wip` action uses the `github.event.pull_request.title` parameter in an insecure way. The title parameter is used in a run statement - resulting in a command injection vulnerability due to string interpolation.

## Details and Impact
This vulnerability can be triggered by any user on GitHub. They just need to create a pull request with a commit message containing an exploit. (Note that first-time PR requests will not be run - but the attacker can submit a valid PR before submitting an invalid PR). The commit can be genuine, but the commit message can be malicious. 

This can be used to execute code on the GitHub runners (potentially use it for crypto-mining, and waste your resources) and can be used to exfiltrate any secrets that you use in the CI pipeline (including repository tokens). [Here](https://securitylab.github.com/research/github-actions-untrusted-input/) is a set of blog posts by Github's security team explaining this issue.

## How to update existing workflows

Replace the following line in your workflow using this action with the `v2` branch name or commit pointing to this branch:

```yaml
    uses: embano1/wip@v2
```

Or using the exact commit:

```yaml
    uses: embano1/wip@c25450f77ed02c20d00b76ee3b33ff43838739a2 # v2
```

## References
- https://github.com/embano1/wip/security/advisories/GHSA-rg3q-prf8-qxmp
- https://nvd.nist.gov/vuln/detail/CVE-2023-30623
- https://github.com/embano1/wip/commit/c25450f77ed02c20d00b76ee3b33ff43838739a2
- https://github.com/embano1/wip
- https://securitylab.github.com/research/github-actions-untrusted-input

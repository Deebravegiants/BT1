# [M] Private data leak on login-required Discourse sites

## Summary
Severity: Medium
Advisory: CVE-2025-46813
Aliases: GHSA-v3h7-c287-pfg9
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/CVE-2025-46813
Type: osv

## Details
Discourse is an open-source community platform. A data leak vulnerability affects sites deployed between commits 10df7fdee060d44accdee7679d66d778d1136510 and 82d84af6b0efbd9fa2aeec3e91ce7be1a768511b. On login-required sites, the leak meant that some content on the site's homepage could be visible to unauthenticated users. Only login-required sites that got deployed during this timeframe are affected, roughly between April 30 2025 noon EDT and May 2 2025, noon EDT. Sites on the stable branch are unaffected. Private content on an instance's homepage could be visible to unauthenticated users on login-required sites. Versions of 3.5.0.beta4 after commit 82d84af6b0efbd9fa2aeec3e91ce7be1a768511b are not vulnerable to the issue. No workarounds are available. Sites must upgrade to a non-vulnerable version of Discourse.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46813.json
- https://github.com/discourse/discourse/security/advisories/GHSA-v3h7-c287-pfg9
- https://nvd.nist.gov/vuln/detail/CVE-2025-46813
- https://github.com/discourse/discourse/commit/10df7fdee060d44accdee7679d66d778d1136510
- https://github.com/discourse/discourse/commit/82d84af6b0efbd9fa2aeec3e91ce7be1a768511b

# [M] mise: Incorrect file ownership, when installed by the root user using `install.sh`

## Summary
Severity: Medium
Advisory: CVE-2026-71477
Aliases: GHSA-9mm4-fgvc-x7rp
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-71477
Type: osv

## Details
mise manages dev tools like node, python, cmake, and terraform. Prior to 2026.7.1, release tar archives record mise/bin/mise with user and group ID 1001 and packaging/standalone/install.envsubst extracts and moves it without normalizing ownership, allowing a local user with those IDs to replace a root-installed executable, especially when MISE_INSTALL_PATH targets a shared location such as /usr/local/bin. This issue is fixed in version 2026.7.1.

## References
- https://github.com/jdx/mise/releases/tag/v2026.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71477.json
- https://github.com/jdx/mise/security/advisories/GHSA-9mm4-fgvc-x7rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-71477
- https://github.com/jdx/mise/commit/b65dd674d75d9aa5c038b58a3a0cdb522cf258d5
- https://github.com/jdx/mise/commit/f1c28906f17af74430ff96f4438733c4a842c88d
- https://github.com/jdx/mise/pull/10808
- https://github.com/jdx/mise/pull/10819

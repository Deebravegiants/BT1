# [C] CVE-2020-15272

## Summary
Severity: Critical
Advisory: CVE-2020-15272
Aliases: GHSA-hgx2-4pp9-357g
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2020-10-26
Source: https://osv.dev/vulnerability/CVE-2020-15272
Type: osv

## Details
In the git-tag-annotation-action (open source GitHub Action) before version 1.0.1, an attacker can execute arbitrary (*) shell commands if they can control the value of [the `tag` input] or manage to alter the value of [the `GITHUB_REF` environment variable]. The problem has been patched in version 1.0.1. If you don't use the `tag` input you are most likely safe. The `GITHUB_REF` environment variable is protected by the GitHub Actions environment so attacks from there should be impossible. If you must use the `tag` input and cannot upgrade to `> 1.0.0` make sure that the value is not controlled by another Action.

## References
- https://github.com/ericcornelissen/git-tag-annotation-action/releases/tag/v1.0.1
- https://github.com/ericcornelissen/git-tag-annotation-action/security/advisories/GHSA-hgx2-4pp9-357g
- https://github.com/ericcornelissen/git-tag-annotation-action/commit/9f30756375cc4b1b6c66f274fc9c591fa901455a

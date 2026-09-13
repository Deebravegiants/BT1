# [M] Git does not sanitize URLs when asking for credentials interactively

## Summary
Severity: Medium
Advisory: BIT-git-2024-50349
Aliases: CVE-2024-50349, GHSA-hmg8-h7qf-7cxr
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-git-2024-50349
Type: osv

## Affected
- Bitnami: `git` — affected >=2.48.0 <2.48.1

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. When Git asks for credentials via a terminal prompt (i.e. without using any credential helper), it prints out the host name for which the user is expected to provide a username and/or a password. At this stage, any URL-encoded parts have been decoded already, and are printed verbatim. This allows attackers to craft URLs that contain ANSI escape sequences that the terminal interpret to confuse users e.g. into providing passwords for trusted Git hosting sites when in fact they are then sent to untrusted sites that are under the attacker's control. This issue has been patch via commits `7725b81` and `c903985` which are included in release versions v2.48.1, v2.47.2, v2.46.3, v2.45.3, v2.44.3, v2.43.6, v2.42.4, v2.41.3, and v2.40.4. Users are advised to upgrade. Users unable to upgrade should avoid cloning from untrusted URLs, especially recursive clones.

## References
- https://github.com/git/git/commit/7725b8100ffbbff2750ee4d61a0fcc1f53a086e8
- https://github.com/git/git/commit/c903985bf7e772e2d08275c1a95c8a55ab011577
- https://github.com/git/git/security/advisories/GHSA-hmg8-h7qf-7cxr
- https://nvd.nist.gov/vuln/detail/CVE-2024-50349
- https://lists.debian.org/debian-lts-announce/2025/01/msg00025.html

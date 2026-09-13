# [H] Newline confusion in credential helpers can lead to credential exfiltration in git

## Summary
Severity: High
Advisory: BIT-git-2024-52006
Aliases: CVE-2024-52006
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-git-2024-52006
Type: osv

## Affected
- Bitnami: `git` — affected >=2.48.0 <2.48.1

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. Git defines a line-based protocol that is used to exchange information between Git and Git credential helpers. Some ecosystems (most notably, .NET and node.js) interpret single Carriage Return characters as newlines, which renders the protections against CVE-2020-5260 incomplete for credential helpers that treat Carriage Returns in this way. This issue has been addressed in commit `b01b9b8` which is included in release versions v2.48.1, v2.47.2, v2.46.3, v2.45.3, v2.44.3, v2.43.6, v2.42.4, v2.41.3, and v2.40.4. Users are advised to upgrade. Users unable to upgrade should avoid cloning from untrusted URLs, especially recursive clones.

## References
- https://github.com/git-ecosystem/git-credential-manager/security/advisories/GHSA-86c2-4x57-wc8g
- https://github.com/git/git/commit/b01b9b81d36759cdcd07305e78765199e1bc2060
- https://github.com/git/git/security/advisories/GHSA-qm7j-c969-7j4q
- https://github.com/git/git/security/advisories/GHSA-r5ph-xg7q-xfrp
- https://nvd.nist.gov/vuln/detail/CVE-2024-52006
- https://lists.debian.org/debian-lts-announce/2025/01/msg00025.html

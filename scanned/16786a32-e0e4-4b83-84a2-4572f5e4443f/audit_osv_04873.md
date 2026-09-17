# [H] Git vulnerable to Remote Code Execution while cloning special-crafted local repositories

## Summary
Severity: High
Advisory: BIT-git-2024-32004
Aliases: CVE-2024-32004, GHSA-xfc6-vwr8-r389
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-git-2024-32004
Type: osv

## Affected
- Bitnami: `git` — affected >=2.45.0 <2.45.1

## Details
Git is a revision control system. Prior to versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4, an attacker can prepare a local repository in such a way that, when cloned, will execute arbitrary code during the operation. The problem has been patched in versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4. As a workaround, avoid cloning repositories from untrusted sources.

## References
- https://git-scm.com/docs/git-clone
- https://github.com/git/git/commit/f4aa8c8bb11dae6e769cd930565173808cbb69c8
- https://github.com/git/git/security/advisories/GHSA-xfc6-vwr8-r389
- http://www.openwall.com/lists/oss-security/2024/05/14/2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S4CK4IYTXEOBZTEM5K3T6LWOIZ3S44AR/
- https://lists.debian.org/debian-lts-announce/2024/06/msg00018.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-32004
- https://lists.debian.org/debian-lts-announce/2024/09/msg00009.html

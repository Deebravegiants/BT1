# [C] Git's recursive clones on case-insensitive filesystems that support symlinks are susceptible to Remote Code Execution

## Summary
Severity: Critical
Advisory: BIT-git-2024-32002
Aliases: CVE-2024-32002, GHSA-8h77-4q3w-gfgv
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-git-2024-32002
Type: osv

## Affected
- Bitnami: `git` — affected >=2.45.0 <2.45.1

## Details
Git is a revision control system. Prior to versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4, repositories with submodules can be crafted in a way that exploits a bug in Git whereby it can be fooled into writing files not into the submodule's worktree but into a `.git/` directory. This allows writing a hook that will be executed while the clone operation is still running, giving the user no opportunity to inspect the code that is being executed. The problem has been patched in versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4. If symbolic link support is disabled in Git (e.g. via `git config --global core.symlinks false`), the described attack won't work. As always, it is best to avoid cloning repositories from untrusted sources.

## References
- https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---recurse-submodulesltpathspecgt
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresymlinks
- https://github.com/git/git/commit/97065761333fd62db1912d81b489db938d8c991d
- https://github.com/git/git/security/advisories/GHSA-8h77-4q3w-gfgv
- http://www.openwall.com/lists/oss-security/2024/05/14/2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S4CK4IYTXEOBZTEM5K3T6LWOIZ3S44AR/
- https://lists.debian.org/debian-lts-announce/2024/06/msg00018.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-32002
- https://lists.debian.org/debian-lts-announce/2024/09/msg00009.html

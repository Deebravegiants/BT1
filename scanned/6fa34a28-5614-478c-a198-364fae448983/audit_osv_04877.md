# [H] The sideband payload is passed unfiltered to the terminal in git

## Summary
Severity: High
Advisory: BIT-git-2024-52005
Aliases: CVE-2024-52005, GHSA-7jjc-gg6m-3329
Ecosystem: Bitnami
Published: 2025-04-14
Source: https://osv.dev/vulnerability/BIT-git-2024-52005
Type: osv

## Affected
- Bitnami: `git` — affected >=2.48.0 <2.48.2

## Details
Git is a source code management tool. When cloning from a server (or fetching, or pushing), informational or error messages are transported from the remote Git process to the client via the so-called "sideband channel". These messages will be prefixed with "remote:" and printed directly to the standard error output. Typically, this standard error output is connected to a terminal that understands ANSI escape sequences, which Git did not protect against. Most modern terminals support control sequences that can be used by a malicious actor to hide and misrepresent information, or to mislead the user into executing untrusted scripts. As requested on the git-security mailing list, the patches are under discussion on the public mailing list. Users are advised to update as soon as possible. Users unable to upgrade should avoid recursive clones unless they are from trusted sources.

## References
- https://github.com/git/git/security/advisories/GHSA-7jjc-gg6m-3329
- https://lore.kernel.org/git/1M9FnZ-1taoNo1wwh-00ESSd@mail.gmx.net
- https://nvd.nist.gov/vuln/detail/CVE-2024-52005

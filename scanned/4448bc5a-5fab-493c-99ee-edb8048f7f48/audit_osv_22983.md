# [C] Integer overflow in `git archive`, `git log --format` leading to RCE in git

## Summary
Severity: Critical
Advisory: CVE-2022-41903
Aliases: GHSA-475x-2q3q-hvwq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-41903
Type: osv

## Details
Git is distributed revision control system. `git log` can display commits in an arbitrary format using its `--format` specifiers. This functionality is also exposed to `git archive` via the `export-subst` gitattribute. When processing the padding operators, there is a integer overflow in `pretty.c::format_and_pad_commit()` where a `size_t` is stored improperly as an `int`, and then added as an offset to a `memcpy()`. This overflow can be triggered directly by a user running a command which invokes the commit formatting machinery (e.g., `git log --format=...`). It may also be triggered indirectly through git archive via the export-subst mechanism, which expands format specifiers inside of files within the repository during a git archive. This integer overflow can result in arbitrary heap writes, which may result in arbitrary code execution. The problem has been patched in the versions published on 2023-01-17, going back to v2.30.7. Users are advised to upgrade. Users who are unable to upgrade should disable `git archive` in untrusted repositories. If you expose git archive via `git daemon`, disable it by running `git config --global daemon.uploadArch false`.

## References
- https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes#_export_subst
- https://git-scm.com/docs/pretty-formats#Documentation/pretty-formats.txt-emltltNgttruncltruncmtruncem
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41903.json
- https://github.com/git/git/security/advisories/GHSA-475x-2q3q-hvwq
- https://nvd.nist.gov/vuln/detail/CVE-2022-41903
- https://security.gentoo.org/glsa/202312-15
- https://github.com/git/git/commit/508386c6c5857b4faa2c3e491f422c98cc69ae76

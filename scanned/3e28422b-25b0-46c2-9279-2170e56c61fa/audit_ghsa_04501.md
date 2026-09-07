# [H] skillctl: argument injection, path traversal in --dest, FIFO/device DoS, hardlink exfiltration, and commit-trailer forgery

## Summary
Severity: High
Advisory: GHSA-74p7-6h78-gw8p
CWE: CWE-22, CWE-400, CWE-59, CWE-88, CWE-93
Ecosystem: crates.io
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-74p7-6h78-gw8p
Type: github-advisory

## Affected
- crates.io: `skillctl` — affected >=0 <0.1.3

## Details
## Impact

Following the path-safety patches in [GHSA-wx3m-whqv-xv47](https://github.com/umanio-agency/skillctl/security/advisories/GHSA-wx3m-whqv-xv47) (v0.1.2), a comprehensive multi-angle audit surfaced five further vulnerabilities, now patched in v0.1.3:

1. **`source_sha` argument injection in `git ls-tree` (CRITICAL).** `InstalledSkill.source_sha` deserialized from `.skills.toml` (committed, PR-mergeable) flowed unvalidated into `git ls-tree -r -z <refspec> -- <path>`. Because the refspec sits before `--`, an attacker who slipped a malicious `.skills.toml` into a PR could set `source_sha = "--name-only"` / `--abbrev=0` / `--output=…` and corrupt the diff classifier (which drives `pull` / `push` destructive decisions), or forge a divergence state to trick `push --on-divergence overwrite` into clobbering the wrong content.
2. **FIFO / device / socket denial-of-service in `copy_dir_all` (CRITICAL).** The file-type branch only checked `is_dir()` / `is_symlink()`; a FIFO inside a skill folder fell through to `fs::copy`, which blocks indefinitely waiting for a writer. A character device like `/dev/zero` would read until OOM. Reachable on `skillctl add` against any adversarial library.
3. **`add --dest` arbitrary-directory wipe in agent mode (HIGH).** `--dest` accepted absolute paths and `..` traversal without validation, so a single invocation `skillctl add --dest /Users/victim/.ssh --on-conflict overwrite --skill <maliciously-named>` would `remove_dir_all` arbitrary directories — no `.skills.toml` round-trip required. Reachable in any non-interactive / agent-driven workflow where flag values may be attacker-supplied.
4. **Commit-message trailer forgery via skill names (HIGH).** Skill names were spliced verbatim into `git commit -m "update skill: <name>"` and into the `commit.message` field of `--json` output. A skill named `foo\nCo-Authored-By: evil@x` produced a forged commit trailer that downstream tooling (Linear, GitHub commit-bot, release-notes scrapers) treats as real authorship metadata.
5. **Hardlink exfiltration via the round-trip (HIGH).** `fs::symlink_metadata` reports a regular file for hardlinks (shared inode), and `fs::copy` reads the target content. An untrusted agent writing `<project>/my-skill/data` as a hardlink to `~/.ssh/id_rsa` would have shipped the SSH key content to the (possibly public) library on the next `skillctl push` or `detect`.

## Patches

Fixed in [v0.1.3](https://github.com/umanio-agency/skillctl/releases/tag/v0.1.3):

- `InstalledSkill::validate` rejects any `source_sha` that isn't 40–64 hex characters.
- `fs_util::copy_dir_all` only allows regular files and directories; FIFO / socket / device / other special files are rejected with `AppError::Config`.
- `commands::add::resolve_destination` rejects `..` unconditionally and rejects absolute paths in non-interactive / `--json` mode.
- New `src/sanitize.rs` module: `validate_identifier` (strict, no control bytes / newlines / ESC, used for skill `name` + individual `tags`) and `validate_message_safe` (lenient, allows `\n` + `\t`, rejects `\r` + DEL + C0/C1 controls, used for `description` and `--message`). Wired at the `skill::discover` and `read_tags` boundaries so poisoned skills are dropped silently and poisoned descriptions/tags are stripped from otherwise-valid skills.
- `fs_util::copy_dir_all` checks `metadata.nlink() > 1` on regular files (Unix) and refuses hardlinked content.

All checks are lexical or single-syscall (`symlink_metadata`, `metadata`). No `canonicalize`, no TOCTOU windows. 23 new unit + integration tests cover each rejection class; `cargo test`: 95 pass; clippy clean; `cargo audit` clean.

## Workarounds

Upgrade to v0.1.3. Pre-patch mitigations are awkward but possible:
- Audit every `.skills.toml` `source_sha` field before running `skillctl pull` / `push` / `detect`.
- Audit library content for FIFO / device files and hardlinks before running `skillctl add`.
- Never invoke `skillctl add` with attacker-controllable `--dest` values in agent / CI contexts.
- Never use `--message` with attacker-controlled content.

## Credit

The findings were surfaced by a maintainer-led multi-angle audit (6 parallel sub-agents, one per threat-model dimension) following the firebaguette audit that motivated v0.1.2. The methodology (cross-agent convergence to identify the most exploitable items) is documented in the project's internal decisions log; the strongest signal was the four-of-six independent convergence on the `source_sha` vector.

## Resources

- Fix commit: [28dfce3](https://github.com/umanio-agency/skillctl/commit/28dfce3)
- Release: https://github.com/umanio-agency/skillctl/releases/tag/v0.1.3
- Prior advisory (path-safety + symlinks): [GHSA-wx3m-whqv-xv47](https://github.com/umanio-agency/skillctl/security/advisories/GHSA-wx3m-whqv-xv47)

## References
- https://github.com/umanio-agency/skillctl/security/advisories/GHSA-74p7-6h78-gw8p
- https://github.com/umanio-agency/skillctl/security/advisories/GHSA-wx3m-whqv-xv47
- https://github.com/umanio-agency/skillctl/commit/28dfce3
- https://github.com/umanio-agency/skillctl
- https://github.com/umanio-agency/skillctl/releases/tag/v0.1.3

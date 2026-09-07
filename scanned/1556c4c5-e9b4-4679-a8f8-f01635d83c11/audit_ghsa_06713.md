# [H] Pheditor: Terminal command-allowlist bypass via argument injection leads to RCE — surviving vector after the metacharacter-sanitization fixes

## Summary
Severity: High
Advisory: GHSA-g3hq-hphg-8fhh
CWE: CWE-78, CWE-88
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-g3hq-hphg-8fhh
Type: github-advisory

## Affected
- Packagist: `pheditor/pheditor` — affected >=0 <2.0.7

## Details
### Summary

pheditor's terminal feature restricts callers to an allowlist of commands (`TERMINAL_COMMANDS`) and rejects shell metacharacters. The allowlist is enforced as a PREFIX match with no argument validation, and the allowlist includes binaries that grant arbitrary command execution through their own options (`find`, `git`, `php`, `tar`, `grep`). A caller can therefore run any command using only allowlisted binaries and no rejected metacharacter, escaping the allowlist restriction the terminal feature relies on.

### Relationship to the prior terminal advisories (this is a surviving, distinct vector)

The prior terminal advisories were all shell-metacharacter injections: GHSA-9643-6xjp-vx57 (`$()`), GHSA-wg4w-wr5q-6vjc (`|`, backtick, newline), GHSA-jvc5-58fv-w8cq (`;` via the dir field). The current code rejects those characters. This report is a different class — CWE-88 argument injection through an allowlisted binary's flags — which the metacharacter denylist does not address.

### Root cause (HEAD, v2.0.6)

In the `terminal` action handler of `pheditor.php`:
1. `:588` rejects `&`, `;`, `|`, `$`, backtick, `\n`, `\r`. It does NOT reject space, `-`, `{`, `}`, `+`, `/`, `.`.
2. `:595-605` checks the command against `TERMINAL_COMMANDS` (defined `:25`: `ls,...,php,...,git,find,grep,...,tar,...,composer,exit`) using a PREFIX match: `strlen($command) >= strlen($value) && substr($command, 0, strlen($value)) == $value`. There is no word boundary and no validation of the arguments that follow.
3. `:617` runs the command through the shell unchanged: `shell_exec((empty($dir) ? null : 'cd ' . escapeshellarg($dir) . ' && ') . $command . ' && echo \ ; pwd')`.

So a command beginning with an allowlisted binary, carrying a code-exec flag, and containing none of the rejected characters reaches `shell_exec` intact.

### Proof of concept (reproduced)

POST to the terminal action with:
  command = `find . -maxdepth 0 -exec touch /tmp/PWNED {} +`
  dir = (any)

This contains no rejected metacharacter, prefix-matches the allowlisted `find`, and `find -exec` runs an arbitrary program. A faithful harness mirroring the three guards (`poc/reproduction.sh`, `poc/transcript.txt`) creates the marker file. Other allowlisted-binary payloads with the same property: `git -c alias.x='!touch /tmp/PWNED' x`, `php -r 'system("id");'`, `tar -cf /dev/null --checkpoint=1 --checkpoint-action=exec="touch /tmp/PWNED" .`.

### Impact

Arbitrary command execution on the host, under the web server's privileges, for a caller with the `terminal` permission (enabled in the default configuration). The exposure is amplified by GHSA-p4h7-p9rj-2pq2 (hardcoded default `admin` password with no forced change): a default deployment grants the authenticated access needed to reach the terminal action with a single known credential, making the chain effectively unauthenticated RCE.

### Remediation

Validate the FULL command, not just its prefix: tokenize and require the program to be an allowlisted binary AND constrain its arguments (reject `-exec`/`-execdir` for `find`, `-c`/`--upload-pack` for `git`, `-r`/`-d` for `php`, `--checkpoint-action`/`--to-command` for `tar`, `-f`/`--file` program forms, etc.), or run each command as an argv array through a restricted launcher with no shell, or remove the code-exec-capable binaries from the allowlist. A prefix allowlist over a shell sink cannot constrain capability.

Credit: anir0y (independent security research).

## References
- https://github.com/pheditor/pheditor/security/advisories/GHSA-g3hq-hphg-8fhh
- https://github.com/pheditor/pheditor/commit/f40f5070d5a171b65359bc87568734d31de498e1
- https://github.com/pheditor/pheditor
- https://github.com/pheditor/pheditor/releases/tag/2.0.7

# [H] Joker linter executed project-local .jokerd/linter.* files during linting

## Summary
Severity: High
Advisory: GHSA-m835-3cm9-rggg
Aliases: CVE-2026-59172
Ecosystem: Go
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-m835-3cm9-rggg
Type: osv

## Affected
- Go: `github.com/candid82/joker` — affected >=0 <1.8.2

## Details
## Impact

In Joker versions before 1.8.2, `joker --lint <file>` located a `.jokerd/` directory by walking up from the linted file and executed matching `linter.*` files from that directory before linting. Because these files are executable Joker/Clojure code, linting a file inside an untrusted repository could execute code supplied by that repository.

This could be triggered by editor integrations or CI jobs that automatically run `joker --lint` on checked-out source code.

## Patches

Fixed in Joker v1.8.2. Executable linter customization files are now loaded only from the user's home `.jokerd` directory (`~/.jokerd/linter.cljc`, `~/.jokerd/linter.clj`, `~/.jokerd/linter.cljs`, or `~/.jokerd/linter.joke`). Project-local `.jokerd/linter.*` files are no longer executed.

## Workarounds

Users who cannot upgrade should avoid running `joker --lint` on untrusted repositories, especially through editor integrations or unattended CI. Removing or disabling project-local `.jokerd/linter.*` files before linting also avoids the code-execution path.

## Credits

Reported by Younghun Ko of AhnLab (@koyokr).

## References
- https://github.com/candid82/joker/security/advisories/GHSA-m835-3cm9-rggg
- https://github.com/candid82/joker

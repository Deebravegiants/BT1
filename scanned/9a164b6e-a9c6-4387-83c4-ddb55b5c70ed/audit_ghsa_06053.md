# [M] Open WebUI: Any authenticated user can stall a worker via a knowledge-search pattern that backtracks catastrophically

## Summary
Severity: Medium
Advisory: GHSA-2f54-p244-32q6
CVE: CVE-2026-70493
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-2f54-p244-32q6
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.6 <0.11.0

## Details
## Summary
The built-in knowledge search tools let a chat participant choose the pattern used to grep knowledge files. Patterns containing regex metacharacters were compiled with Python's backtracking `re` engine and run against every line of every reachable file, with no time limit anywhere on that path. A single crafted pattern and a single short line of matching text pin one CPU core for as long as the attacker wants, and because the search runs synchronously inside the event loop, that worker serves nobody else while it spins.

## Preconditions
- Default configuration. The knowledge builtin tool group is enabled by default, and with `ENABLE_KB_EXEC` at its default of `False` the model is handed `grep_knowledge_files`, which is the affected path.
- Any authenticated user, no elevated role and no workspace permission.
- One file the attacker can read. `USER_PERMISSIONS_CHAT_FILE_UPLOAD` defaults to true and a user always has read access to their own upload, so both halves of the input are attacker-supplied.
- A model willing to call the tool with the attacker's literal pattern. This is the one non-deterministic step: it is reliable in practice by instructing the model in your own chat, but it is not guaranteed on a given turn.
- Deployments running with `UVICORN_WORKERS` at its default of 1 lose the whole instance; multi-worker deployments lose one worker per request.

## Impact
Availability, against every other user of the affected worker. Cost scales exponentially with the length of the matching text: measured on the vulnerable code, a 24 character subject takes 1.2s, 28 takes 19s and 30 takes 74s, and a 40 character subject extrapolates to roughly a day of CPU. The same subject against a literal pattern takes under a microsecond. There is no confidentiality or integrity effect, and no data is read or altered.

## Fix
Fixed in 0.11.0 by https://github.com/open-webui/open-webui/pull/27471. Pattern matching moved from `re` to the `regex` engine, which supports a per-search timeout, and every tool call now runs its searches under a single 2 second matching budget, after which the tool returns an error instead of continuing to match. Upgrading is sufficient; there is nothing an operator has to configure.

## Root cause
- `backend/open_webui/tools/knowledge_fs.py`, `build_matcher`: compiled the caller's pattern and returned an unbounded match function.
- `backend/open_webui/tools/builtin.py`, `grep_knowledge_files`: the default-configuration caller, which ran that matcher over every line of every reachable file.

`build_matcher` treated any pattern containing regex metacharacters as a regex, so no explicit flag was needed to reach the compiler. From there the only limits in place were on results, not on work: a cap on matches returned and a cap on files scanned, neither of which bounds the time a single line can consume. Backtracking cost is exponential in the length of the matched text rather than in the pattern, so capping pattern length or line length would not have bounded it either. The engine had no timeout available and none was imposed elsewhere.

## Proof of concept
Against a real instance as an ordinary user:

1. Upload a text file whose content is a single line of 30 `x` characters, and no `y`.
2. In a chat on a model with the knowledge tools available, instruct the model to call `grep_knowledge_files` with the pattern `(x|x)*y` and that file's id.
3. The request never returns. The worker's CPU sits at 100% for the duration, and concurrent requests from other users on the same worker do not complete.

Growth measured directly against `build_matcher` on the vulnerable code:

| subject length | time  |
| -------------- | ----- |
| 16             | 4.7ms |
| 20             | 73ms  |
| 24             | 1.21s |
| 28             | 19.3s |
| 30             | 73.9s |

## Credits
@Classic298, for the finding and the fix.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-2f54-p244-32q6
- https://github.com/open-webui/open-webui/pull/27471
- https://github.com/open-webui/open-webui/commit/3ab2026262ef6f09810e4d235c5f9a9cb903e595
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0

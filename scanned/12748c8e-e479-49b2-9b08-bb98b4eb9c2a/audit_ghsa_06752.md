# [M] oasdiff does not enforce --allow-external-refs=false on the git-revision load path (SSRF / local file read)

## Summary
Severity: Medium
Advisory: GHSA-2jcc-mxv7-p3f9
CVE: CVE-2026-53508
CWE: CWE-693, CWE-73, CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-2jcc-mxv7-p3f9
Type: github-advisory

## Affected
- Go: `github.com/oasdiff/oasdiff` — affected >=1.13.2 <1.18.1

## Details
## Summary

From **v1.13.2** through **v1.18.0**, oasdiff did not enforce `--allow-external-refs=false` (library: `openapi3.Loader.IsExternalRefsAllowed = false`) when loading a spec from a **git revision** (the `rev:path` form, e.g. `main:openapi.yaml`). External `$ref`s were resolved on that load path even when external refs were explicitly disabled, so the mitigation silently did not apply there.

## Impact

A caller who set `--allow-external-refs=false` *specifically to safely process untrusted specs* remained exposed — on the git-revision load path only — to:

- **SSRF** via `$ref: "http://<internal-host>/…"`, and
- **Local file reads** via `$ref: "/path"` or `file://`.

Affected callers:

- **CLI:** `oasdiff diff main:openapi.yaml HEAD:openapi.yaml --allow-external-refs=false` (and `breaking` / `changelog` / `summary`, and the `git-diff-driver`) run over untrusted spec content.
- **Go library consumers** of `github.com/oasdiff/oasdiff/load` that set `IsExternalRefsAllowed = false` and load from a git-revision source via `load.NewSpecInfo`.

The file and URL load paths correctly enforced the setting; only the git-revision path was affected. Callers that left external refs at the default (`true`) are not in scope for *this* advisory.

## Patches

**v1.18.1** enforces the external-refs policy on the git-revision path (so `--allow-external-refs=false` now blocks external `$ref`s there) and returns a dedicated exit code (`123`) when an external `$ref` is refused.

## Workarounds

- Upgrade to **v1.18.1**, or
- Avoid the git-revision input form when processing untrusted specs with external refs disabled.

## Notes

- Introduced in **v1.13.2** (#832, which added `$ref`-chain resolution on the git-revision path); fixed in **v1.18.1** (#974, #975).
- The permissive **default** (`allow-external-refs: true`) and its zero-interaction exposure in CI via the GitHub Action is tracked separately in GHSA-fhj3-7267-7vv5 (oasdiff-action).

## References
- https://github.com/oasdiff/oasdiff/security/advisories/GHSA-2jcc-mxv7-p3f9
- https://github.com/oasdiff/oasdiff/pull/832
- https://github.com/oasdiff/oasdiff/pull/974
- https://github.com/oasdiff/oasdiff/pull/975
- https://github.com/oasdiff/oasdiff

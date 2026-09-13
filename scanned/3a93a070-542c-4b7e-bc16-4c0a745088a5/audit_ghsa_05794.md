# [H] Copier has a trust-prefix bypass via path traversal that runs tasks unprompted

## Summary
Severity: High
Advisory: GHSA-9gmc-jqmh-3rvm
CVE: CVE-2026-53951
CWE: CWE-22, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-9gmc-jqmh-3rvm
Type: github-advisory

## Affected
- PyPI: `copier` — affected >=9.5.0 <9.15.2

## Details
# Copier: trust-prefix bypass via path traversal runs tasks unprompted

### Summary

In copier `>= 9.5.0, <= 9.15.1`, the `trust` setting's prefix match
(`copier/_settings.py`) compares the template URL against a trusted prefix with
a raw `str.startswith` and **no path normalization**, while the URL *is*
normalized when the template is actually fetched (`Path.resolve()` for local
paths; libcurl dot-segment removal for `https`). A template reference that
textually starts with a trusted prefix but contains `..`
(e.g. `https://github.com/trusted-org/../attacker-org/repo.git`) is therefore
granted trust yet resolves to a different, attacker-controlled template, whose
`tasks` / `migrations` / `jinja_extensions` then run **without the `--trust`
prompt** — arbitrary command execution. Likely **CWE-22 (Improper Limitation of
a Pathname)** in the trust check leading to **CWE-94 (code execution)**.

### Details

`trust` lets users mark template locations as trusted so copier skips the
unsafe-feature gate. A trailing `/` makes an entry a **prefix** match
(`docs/settings.md`: *"Locations ending with `/` will be matched as prefixes,
trusting all templates from that location"*).

`copier/_settings.py:141-146` (tag `v9.15.1`):

```python
    return any(
        repository.startswith(_normalize(t))
        if t.endswith("/")
        else repository == _normalize(t)
        for t in trust
    )
```

`_normalize` only expands `~`; it does **not** touch `..` or collapse segments —
`copier/_settings.py:149-152` (tag `v9.15.1`):

```python
def _normalize(url: str) -> str:
    if url.startswith("~"):  # Only expand on str to avoid messing with URLs
        url = expanduser(url)  # noqa: PTH111
    return url
```

This decision gates code execution — `copier/_main.py:293` (tag `v9.15.1`):

```python
        if self.unsafe or is_trusted_repository(self.settings.trust, self.template.url):
            return  # skip the unsafe-feature check entirely
```

The chain: the trust comparison sees the **raw** URL, so
`"https://github.com/safeorg/../evilorg/t.git".startswith("https://github.com/safeorg/")`
is `True`; but the value copier hands to `git`/`pathlib` is **normalized**, so
the template actually loaded is `evilorg/t` (a different, attacker-owned org).
Trust is granted to a location the user never trusted, and `_check_unsafe`
returns early, so the malicious template's tasks execute with no prompt.

This is most acute on `copier update`, which reads `_src_path` from the
project's `.copier-answers.yml` (`copier/_subproject.py`) — i.e. an attacker who
hands you a project controls the URL that the trust check is applied to.

In-repo asymmetry that confirms the omission: copier consistently resolves
paths *everywhere else* it makes a security decision — `Path.resolve()` plus
`is_relative_to(...)` guards in `_render_template`, `template_copy_root`, and
`_external_data` — but not in the trust comparison.

### PoC

Self-contained standalone script; runs against a clean, pinned PyPI install via
the real `copier` CLI only. **Static by default** (`copier copy --pretend`
reaches the trust decision but does not execute tasks); `--prove-exec` is an
opt-in supplementary run that fires an inert marker (`echo` + `touch`). The full
`poc.py` accompanies this report.

Build and run:

```bash
python -m venv venv && . venv/bin/activate
pip install "copier==9.15.1"
python poc.py                # static proof (default)
python poc.py --prove-exec   # also fire the inert marker
```

Observed output (`copier 9.15.1`):

```
== version proof ==
  copier == 9.15.1
  module : .../site-packages/copier/__init__.py

== inputs ==
  trusted prefix (settings.yml): /tmp/copier_trust_poc_XXXX/trusted_templates/
  control src (canonical)      : /tmp/copier_trust_poc_XXXX/attacker/evil_template
  exploit src (traversal)      : /tmp/copier_trust_poc_XXXX/trusted_templates/../attacker/evil_template
  both resolve to the SAME dir : True
  exploit startswith trusted/  : True
  minimal delta                : exploit = '/tmp/copier_trust_poc_XXXX/trusted_templates/..' + '/attacker/evil_template'

== static proof (copier copy --pretend; payload NOT executed) ==
  control (canonical, untrusted): exit=4  -> BLOCKED (UnsafeTemplateError)
  exploit (trusted-prefix /..)  : exit=0  -> TRUSTED, task reached
  marker on disk after --pretend: False (expected False: --pretend does not run tasks)

  --- copier's own output for the exploit (note the task it WOULD run) ---
  | Copying from template version None
  |     create  hello.txt
  |  > Running task 1 of 1: echo COPIER-TRUST-BYPASS-RCE-MARKER && touch COPIER_RCE_PROOF

== VERDICT ==
  BYPASS CONFIRMED: identical template is refused by canonical path
  (exit 4) yet granted trust via '<trusted>/..' traversal (exit 0),
  so its tasks run with no --trust prompt.

== --prove-exec: running the exploit for real (inert marker) ==
  | COPIER-TRUST-BYPASS-RCE-MARKER
  |  > Running task 1 of 1: echo COPIER-TRUST-BYPASS-RCE-MARKER && touch COPIER_RCE_PROOF
  exit=0  marker file 'COPIER_RCE_PROOF' created: True
  -> ARBITRARY COMMAND EXECUTED via a 'trusted' template, no --trust
```

The exploit is the same template as the control plus the minimal delta
`<trusted_prefix>/..`. Deterministic: same input → same result. The PoC uses a
local trusted prefix for a self-contained, network-free run; the `https` case is
identical because git normalizes `..` before the request — e.g.
`git ls-remote "https://github.com/copier-org/../pallets/flask.git"` emits
`warning: redirecting to https://github.com/pallets/flask.git/` and returns
`pallets/flask`'s refs, a different org than the trusted `copier-org/`.

### Impact

A user who has configured a trusted **prefix** (a trailing-`/` entry in
`trust`, a documented feature) no longer gets the unsafe-feature prompt for a
template that merely *appears* to live under that prefix. Any party who can
influence the template URL — most realistically the author of a project the
victim runs `copier update` on, since `_src_path` comes from that project's
`.copier-answers.yml` — can host the real template under a different
org/location reached via `..` and have its `tasks`/`migrations`/
`jinja_extensions` execute arbitrary commands with no prompt. It fires on a
default, modern git for both local paths and `https`.

Proposed severity: **High**, comparable to the project's prior unsafe-template
advisory (GHSA-3xw7-v6cj-5q8h). Proposed CVSS v4 vector (maintainer to finalize;
`AT:P` reflects the required trusted-prefix configuration):
`CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H`. Conservative
variant if you scope impact to the user account only (no host escape claim):
drop `SC/SI/SA` to `N`.

### Recommended fix

Normalize **both** sides before comparing, instead of raw `startswith`. For
local entries, compare resolved absolute paths (`Path(t).resolve()` vs
`Path(repository).resolve()`) using segment containment / `is_relative_to`, the
pattern already used in `_render_template` and `template_copy_root`. For URL
entries, parse the URL and reject or collapse `..`/`.`/empty path segments
before the prefix test. As defense-in-depth, reject any `_src_path` read from an
answers file that contains `..` segments after the scheme/host, since
legitimate template URLs never need them.

### References

- CWE-22 — https://cwe.mitre.org/data/definitions/22.html
- CWE-94 — https://cwe.mitre.org/data/definitions/94.html
- Affected source (tag `v9.15.1`): `copier/_settings.py:141-146` (prefix match),
  `copier/_settings.py:149-152` (`_normalize`), `copier/_main.py:293` (trust gate).
- Documented prefix behavior: `docs/settings.md` ("Locations ending with `/`
  will be matched as prefixes").
- `https` `..` normalization: libcurl removes dot segments by default
  (`CURLOPT_PATH_AS_IS` defaults to off) — https://curl.se/libcurl/c/CURLOPT_PATH_AS_IS.html
- Novelty: distinct from copier's published advisories, which concern filesystem
  read/write traversal in rendered output; this is an authorization bypass in
  the `trust` setting's URL matching. The flawed match is identical between
  released `v9.15.1` and current `master` HEAD, and unchanged since the
  trust-prefix feature was introduced in `v9.5.0` (originally `copier/settings.py`,
  commit `71358ed`; renamed to `copier/_settings.py` in the v9.12.0 refactor).

## References
- https://github.com/copier-org/copier/security/advisories/GHSA-9gmc-jqmh-3rvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53951
- https://github.com/copier-org/copier
- https://github.com/copier-org/copier/releases/tag/v9.15.2

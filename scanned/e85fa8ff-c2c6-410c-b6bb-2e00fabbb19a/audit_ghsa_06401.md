# [H] NLTK: Uncontrolled search path when invoking the Graphviz 'dot' binary

## Summary
Severity: High
Advisory: GHSA-6hwm-xvph-95vm
CVE: CVE-2026-78680
CWE: CWE-426, CWE-427
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-6hwm-xvph-95vm
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.3

## Details
Two NLTK sites executed the Graphviz `dot` program by bare name, so process creation resolved it via the search path — and on Windows via the current working directory — rather than a validated absolute location. An attacker who can place a file named `dot` where resolution looks (the CWD on Windows, or a writable/relative entry such as `.` on `PATH`) has their binary executed in place of Graphviz (arbitrary code execution).

Affected (<= 3.10.2):
- `nltk.parse.dependencygraph.dot2img` — called `find_binary("dot")` but discarded the returned validated path and then ran the bare name `["dot", ...]`, so the validation had no effect.
- `nltk.translate.api.AlignedSent._repr_svg_` — ran the bare name with no validation at all (IPython SVG rendering).

This is the same class already fixed for the senna, weka, boxer, malt, repp and hunpos wrappers. `nltk.internals.find_binary` refuses a CWD-relative match for a bare tool name and returns only a trusted absolute path; the fix runs that path in both sites.

---

## Attack demonstration
Captured output, not illustrative. A `./dot` that writes a `PWNED` marker, planted in the CWD with `.` prepended to `PATH`.

**The vulnerable behaviour (old bare-name exec):**
```
Control (OLD behavior) — bare ['dot'] in this dir with '.' on PATH:
  bare ['dot'] executed planted binary = True
```

**The patched functions refuse it:**
```
FIXED code, with ./dot planted and '.' on PATH:
  dependencygraph.dot2img : Exception "Cannot find the dot binary..."  | planted-binary-executed=False  safe
  AlignedSent._repr_svg_  : Exception "Cannot find the dot binary..."  | planted-binary-executed=False  safe
```

**And `find_binary` itself was attacked directly** (the fix trusts nothing else):
```
Attack 1: ./dot in CWD, no dot on PATH            -> LookupError (refused)  safe
Attack 2: ./dot/dot (dir 'dot' holding 'dot')     -> LookupError (refused)  safe
Attack 3: '.' on PATH + ./dot                     -> LookupError (refused)  safe
Attack 4: attacker-writable ABSOLUTE dir on PATH  -> returned /…/evilbin/dot (absolute)
```
Attack 4 is out of scope: trusting an absolute directory that is already on `PATH` is the operating system's own trust model — an attacker who can write to a `PATH` directory owns the account regardless of NLTK. `find_binary` defends specifically against the CWD/relative injection that bare-name exec is vulnerable to (attacks 1–3), which is exactly what this fix inherits.

Environment: python 3.13.7. `dot` is not required to reproduce — the planted binary is the payload.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-6hwm-xvph-95vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-78680
- https://github.com/nltk/nltk/commit/1a3cd1764ab3deb084fb66d0ffb4873717659538
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.3
- https://www.vulncheck.com/advisories/nltk-before-arbitrary-code-execution-via-graphviz-dot-binary

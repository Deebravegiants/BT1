# [M] Mistune directives/include: mutual `.. include::` recursion crashes the renderer with `RecursionError`, denial of service via two attacker-controlled markdown files

## Summary
Severity: Medium
Advisory: GHSA-8mpj-m6qm-5qr8
CVE: CVE-2026-59927
CWE: CWE-674, CWE-755
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8mpj-m6qm-5qr8
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
## Summary

**Type:** Uncontrolled recursion via mutual include. The `Include` directive checks for direct self-reference (`a.md` cannot include `a.md`), but does not detect indirect cycles. Two markdown files that include each other (`a.md` → includes `b.md` → includes `a.md`) cause unbounded recursion until Python's stack limit fires `RecursionError`. The exception propagates out of the renderer and crashes the calling code.
**File:** `src/mistune/directives/include.py`, lines 33-37 (the self-include check is the only cycle-detection logic).
**Root cause:** the include logic only compares `os.path.abspath(dest) == os.path.abspath(source_file)`. There is no per-render set of "files already included" that would catch transitive cycles. When `a.md` includes `b.md`, the recursive `block.parse(new_state)` call uses `dest` (b.md) as the new `__file__`, which then includes `a.md` (passing the self-check, because the immediate parent file is `b.md`, not `a.md`), which then includes `b.md`, and so on. Each recursion level adds Python frames; the default stack limit of 1000 frames trips after ~7-10 cycle iterations and Python raises `RecursionError`. Since the directive does not catch the exception, it propagates out of `Markdown.parse()` and surfaces in the calling code, crashing the request.

## Affected Code

**File:** `src/mistune/directives/include.py`, lines 28-54.

```python
relpath = self.parse_title(m)
dest = os.path.join(os.path.dirname(source_file), relpath)
dest = os.path.normpath(dest)

if os.path.abspath(dest) == os.path.abspath(source_file):       # <-- only catches direct self-include
    return {"type": "block_error", "raw": "Could not include self: " + relpath}

if not os.path.isfile(dest):
    return {"type": "block_error", "raw": "Could not find file: " + relpath}

with open(dest, "rb") as f:
    content = f.read().decode(encoding)

ext = os.path.splitext(relpath)[1]
if ext in {".md", ".markdown", ".mkd"}:
    new_state = block.state_cls()
    new_state.env["__file__"] = dest
    new_state.process(content)
    block.parse(new_state)                                       # <-- recursive parse, no cycle tracking
    return new_state.tokens
```

**Why it's wrong:** the cycle-detection check is one level deep. Multi-file cycles slip through trivially. Python's default recursion limit is 1000 frames, so a cycle of length 2 trips after a few hundred mutual includes; the exception is uncaught by the directive, propagating out of `Markdown.__call__()` and crashing whatever called it.

## Exploit Chain

1. Application uses mistune with the `Include` directive enabled. Application accepts user-supplied markdown files (CMS, wiki, multi-user documentation platform, note-taking app, CI/CD doc renderer).
2. Attacker uploads two markdown files:
   - `a.md`: `.. include:: b.md`
   - `b.md`: `.. include:: a.md`
3. Renderer is invoked on `a.md` (or any markdown that references this pair). `Include` directive includes `b.md`, which includes `a.md`, which includes `b.md`, ... Each recursion adds Python frames.
4. After ~340 cycle iterations (depending on default `sys.setrecursionlimit(1000)` and the per-include frame depth), Python raises `RecursionError: maximum recursion depth exceeded`.
5. The exception is not caught by the directive. It propagates through `block.parse`, through `Markdown.__call__`, and into the application's request handler. If the application doesn't catch it explicitly, the request errors out (HTTP 500 in web contexts, crash in CLI tools).

## Security Impact

**Attacker capability:** crash the rendering engine on demand by submitting any markdown that triggers the cycle. Repeated requests deny service. If the renderer is used in a hot path (per-page-view docs rendering, search-index regeneration, scheduled doc-export jobs), the cycle persists across the whole pipeline.
**Preconditions:** application uses mistune with the `Include` directive enabled and renders user-supplied markdown that can reference other user-uploaded files. Attacker needs write access to two .md files in the include search path (or a single file including a known-recurring pair).
**Differential:** PoC-verified against mistune@3.2.1:

```python
import os, mistune
from mistune.directives import RSTDirective, Include

os.makedirs('/tmp/mistune-recur', exist_ok=True)
with open('/tmp/mistune-recur/a.md', 'w') as f:
    f.write('A\n\n.. include:: b.md')
with open('/tmp/mistune-recur/b.md', 'w') as f:
    f.write('B\n\n.. include:: a.md')

md = mistune.create_markdown(plugins=[RSTDirective([Include()])])
state = md.block.state_cls()
state.env['__file__'] = '/tmp/mistune-recur/a.md'
md.parse('.. include:: b.md', state=state)
# RecursionError: maximum recursion depth exceeded
```

The patched build (with the suggested fix below) returns a `block_error` token like the existing self-include check, instead of recursing forever.

## Suggested Fix

Track included paths in `state.env` and reject any include that would re-enter a path already on the include stack:

```diff
--- a/src/mistune/directives/include.py
+++ b/src/mistune/directives/include.py
@@ -28,8 +28,18 @@ class Include(DirectivePlugin):
         relpath = self.parse_title(m)
-        dest = os.path.join(os.path.dirname(source_file), relpath)
-        dest = os.path.normpath(dest)
+        base = os.path.realpath(os.path.dirname(source_file))
+        dest = os.path.realpath(os.path.join(base, relpath))
+
+        # Track include stack across recursive parses to detect cycles.
+        include_stack = state.env.setdefault("__include_stack__", [])
+        if dest in include_stack or dest == os.path.realpath(source_file):
+            return {
+                "type": "block_error",
+                "raw": "Could not include (cycle): " + relpath,
+            }

-        if os.path.abspath(dest) == os.path.abspath(source_file):
-            return {
-                "type": "block_error",
-                "raw": "Could not include self: " + relpath,
-            }
@@ ... in the markdown-include branch ...
+        include_stack.append(dest)
+        try:
+            new_state = block.state_cls()
+            new_state.env["__file__"] = dest
+            new_state.env["__include_stack__"] = include_stack
+            new_state.process(content)
+            block.parse(new_state)
+            return new_state.tokens
+        finally:
+            include_stack.pop()
```

This catches cycles of any length (`a → b → a`, `a → b → c → a`, etc.). Pair this with the path-containment fix from the LFI advisory and the HTML-extension fix from the include-XSS advisory; together those three patches make the `Include` directive safe to enable on user-supplied markdown.

Add a regression test asserting that a 2-cycle and a 3-cycle both produce `block_error` rather than `RecursionError`.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-8mpj-m6qm-5qr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-59927
- https://github.com/lepture/mistune/commit/1bef343ade163fc3bb95572b15be720084cdb993
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2215.yaml

# [?] release(runway): cherry-pick chore: bump `dompurify` to `3.4.13` to clear `GHSA-55q2-fjhq-7xh7` (#45377)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-08-10
Source: https://github.com/MetaMask/metamask-extension/commit/a70b6f95abc9bd9cf01166410c80a3899634778f
Type: security-commit

## Details
release(runway): cherry-pick chore: bump `dompurify` to `3.4.13` to clear `GHSA-55q2-fjhq-7xh7` (#45377)

- chore: bump `dompurify` to `3.4.13` to clear `GHSA-55q2-fjhq-7xh7`
cp-13.43.0 (#45364)

## **Description**

`dompurify` is a direct production dependency.
[GHSA-55q2-fjhq-7xh7](https://github.com/advisories/GHSA-55q2-fjhq-7xh7)
covers `<= 3.4.12` — during `IN_PLACE` sanitization a hook that removes
an element leaves that element's detached descendants executable,
because `_sanitizeElements()` returns early without calling
`_neutralizeSubtree()`.

**This is not a plain version bump.** `dompurify` was declared *as a
patch spec* in both `dependencies` and `resolutions`, each hard-pinning
the exact version 3.4.12, so `yarn up dompurify` cannot move it. Three
things change together:

- the dependency spec → `patch:dompurify@npm%3A3.4.13#...`
- the matching `resolutions` entry
- the patch itself, rebased 3.4.12 → 3.4.13 via `yarn patch` / `yarn
patch-commit`

**The carried-forward patch is unrelated to this advisory** — it
rewrites `'<!-->'` and `'<!---->'` as concatenations so the literals do
not trip LavaMoat's `SES_HTML_COMMENT_REJECTED`. Same two edits, only
line offsets moved:

```diff
-      dirty = '<!-->';
+      // Modifying to avoid lavamoat SES_HTML_COMMENT_REJECTED
+      dirty = '<!' + '--' + '>';
-      body = _initDocument('<!---->');
+      // Modifying to avoid lavamoat SES_HTML_COMMENT_REJECTED
+      body = _initDocument('<!' + '--' + '--' + '>');
```


_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/a70b6f95abc9bd9cf01166410c80a3899634778f_

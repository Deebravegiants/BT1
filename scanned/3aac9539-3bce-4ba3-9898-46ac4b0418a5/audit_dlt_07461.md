# [?] CI: accept RUSTSEC-2026-0269 and patch fast-uri in the docs-preview lock.

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-09-04
Source: https://github.com/RaoFoundation/subtensor/commit/4129474459bf0b597682ff2cd0c2b889357f6c9c
Type: security-commit

## Details
CI: accept RUSTSEC-2026-0269 and patch fast-uri in the docs-preview lock.

cargo audit: wasmtime 8.0.1 (pinned by the polkadot-sdk fork's sc-executor,
like the other wasmtime entries) picked up RUSTSEC-2026-0269, a WASI
filesystem sandbox escape. The runtime WASM never gets a filesystem, so the
advisory is accepted alongside the existing wasmtime ignores.

docs preview: npm audit flagged fast-uri 3.1.5 (four GHSAs) under the Vercel
CLI tree. Pin fast-uri 3.1.7 via overrides; npm ci and npm audit
--audit-level=high pass locally.

Both checks have been failing on main.

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### .github/workflows/cargo-audit.yml
```diff
@@ -72,6 +72,9 @@ jobs:
           # RUSTSEC-2026-0258: h2 unbounded empty DATA frames. Fix is
           #   >=0.4.16; we still carry 0.3.27 (no 0.3 patch) via hyper in the
           #   fork tree — revisit when that stack moves off h2 0.3.
+          # RUSTSEC-2026-0269: wasmtime 8.0.1 filesystem sandbox escape via
+          #   trailing slashes in WASI paths. We never expose a filesystem to
+          #   the runtime WASM; same pin as the wasmtime entries above.
           cargo audit --ignore RUSTSEC-2023-0091 \
                       --ignore RUSTSEC-2024-0438 \
                       --ignore RUSTSEC-2025-0009 \
@@ -103,4 +106,5 @@ jobs:
                       --ignore RUSTSEC-2025-0020 \
                       --ignore RUSTSEC-2026-0177 \
                       --ignore RUSTSEC-2026-0235 \
-                      --ignore RUSTSEC-2026-0258
+                      --ignore RUSTSEC-2026-0258 \
+                      --ignore RUSTSEC-2026-0269
```

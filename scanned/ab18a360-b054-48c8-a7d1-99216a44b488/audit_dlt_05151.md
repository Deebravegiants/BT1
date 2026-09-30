# [?] Ignore RUSTSEC-2026-0258 until the fork tree leaves h2 0.3.

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-08-18
Source: https://github.com/RaoFoundation/subtensor/commit/00a05e9381f3594d1d57310291eb1529ee7b6d5e
Type: security-commit

## Details
Ignore RUSTSEC-2026-0258 until the fork tree leaves h2 0.3.

The new h2 empty-DATA advisory only has a 0.4.16 fix; 0.3.27 has no patch and is still pulled in by hyper in the polkadot-sdk stack.

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### .github/workflows/cargo-audit.yml
```diff
@@ -69,6 +69,9 @@ jobs:
           # RUSTSEC-2026-0235: rkyv 0.7.x OOB via Rc/Arc metadata; 0.7 unsupported
           #   upstream (fix is >=0.8.17). Pinned by the polkadot-sdk / wasmtime
           #   tree — revisit on the next major SDK bump.
+          # RUSTSEC-2026-0258: h2 unbounded empty DATA frames. Fix is
+          #   >=0.4.16; we still carry 0.3.27 (no 0.3 patch) via hyper in the
+          #   fork tree — revisit when that stack moves off h2 0.3.
           cargo audit --ignore RUSTSEC-2023-0091 \
                       --ignore RUSTSEC-2024-0438 \
                       --ignore RUSTSEC-2025-0009 \
@@ -99,4 +102,5 @@ jobs:
                       --ignore RUSTSEC-2025-0137 \
                       --ignore RUSTSEC-2025-0020 \
                       --ignore RUSTSEC-2026-0177 \
-                      --ignore RUSTSEC-2026-0235
+                      --ignore RUSTSEC-2026-0235 \
+                      --ignore RUSTSEC-2026-0258
```

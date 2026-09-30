# [?] fix: metrics endpoint crashes when it 404s (#763)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2024-03-29
Source: https://github.com/ponder-sh/ponder/commit/80b8e26b7b138ed4b0e84af16e203013580f5b0c
Type: security-commit

## Details
fix: metrics endpoint crashes when it 404s (#763)

* fix: metrics endpoint crashes when it 404s

* chore: changeset

---------

Co-authored-by: typedarray <90073088+0xOlias@users.noreply.github.com>

## Patch
### .changeset/strong-oranges-change.md
```diff
@@ -0,0 +1,5 @@
+---
+"@ponder/core": patch
+---
+
+Fixed a bug where malformed requests to the `/metrics` path could cause the process to exit.
```

### packages/core/src/server/service.ts
```diff
@@ -120,6 +120,7 @@ export class ServerService {
     return async (req, res) => {
       if (req.method !== "GET" && req.method !== "POST") {
         res.status(404).end();
+        return;
       }
 
       try {
```

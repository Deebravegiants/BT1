# [?] fix(config): Do not panic for observability config (#2639)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-09-02
Source: https://github.com/matter-labs/zksync-era/commit/1e768d402012f6c7ce83fdd46c55f830ec31416a
Type: security-commit

## Details
fix(config): Do not panic for observability config (#2639)

## What ❔

<!-- What are the changes this PR brings about? -->
<!-- Example: This PR adds a PR template to the repo. -->
<!-- (For bigger PRs adding more context is appreciated) -->

## Why ❔

<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [ ] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [ ] Code has been formatted via `zk fmt` and `zk lint`.

Signed-off-by: Danil <deniallugo@gmail.com>

## Patch
### core/lib/protobuf_config/src/observability.rs
```diff
@@ -30,11 +30,7 @@ impl ProtoRepr for proto::Observability {
             sentry_url,
             sentry_environment,
             log_format: required(&self.log_format).context("log_format")?.clone(),
-            opentelemetry: self
-                .opentelemetry
-                .as_ref()
-                .map(|cfg| cfg.read().context("opentelemetry"))
-                .transpose()?,
+            opentelemetry: self.opentelemetry.as_ref().and_then(|cfg| cfg.read().ok()),
             log_directives: self.log_directives.clone(),
         })
     }
```

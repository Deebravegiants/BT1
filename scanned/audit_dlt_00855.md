# [?] fix(deny): ignore quick-xml <0.41 XML-parsing DoS advisories (#4883)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-02
Source: https://github.com/matter-labs/zksync-era/commit/622b62c1b0c7cfa8770a0250435f47b02729a612
Type: security-commit

## Details
fix(deny): ignore quick-xml <0.41 XML-parsing DoS advisories (#4883)

cargo-deny fails on RUSTSEC-2026-0194 and RUSTSEC-2026-0195 against
quick-xml 0.37.5. Both are patched in quick-xml >=0.41.0, but it cannot
be bumped: quick-xml is only pulled transitively via sentry ->
sentry-contexts -> os_info -> plist, and no released plist depends on
quick-xml >=0.41.0 yet (latest 1.9.0 caps at ^0.39.2). Bumping
plist/time also requires Rust 1.88, which our pinned nightly-2025-03-19
toolchain lacks.

The DoS vectors are unreachable in our usage: quick-xml is only invoked
by plist to parse local system .plist files for OS-info reporting, not
untrusted network XML. Ignore both advisories with justification.

## What ❔

<!-- What are the changes this PR brings about? -->
<!-- Example: This PR adds a PR template to the repo. -->
<!-- (For bigger PRs adding more context is appreciated) -->

## Why ❔

<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- The `Why` has to be clear to non-Matter Labs entities running their
own ZK Chain -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Is this a breaking change?
- [ ] Yes
- [ ] No

## Operational changes
<!-- Any config changes? Any new flags? Any changes to any scripts? -->
<!-- Please add anything that non-Matter Labs entities running their own
ZK Chain may need to know -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [ ] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [ ] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>

### core/deny.toml
```diff
@@ -39,6 +39,14 @@ ignore = [
   # migrated to rand 0.9. The unsoundness requires a custom logger that calls rand from
   # logging callbacks, which we don't do.
   "RUSTSEC-2026-0097",
+  # `quick-xml` <0.41.0 XML-parsing DoS advisories (quadratic attribute-duplicate check and
+  # unbounded namespace-declaration allocation in `NsReader`). Reached only transitively via
+  # sentry -> sentry-contexts -> os_info -> plist, which parses local system `.plist` files to
+  # report OS info -- not untrusted network input, so the DoS vectors are not reachable for us.
+  # No released `plist` depends on the patched quick-xml >=0.41.0 yet (latest 1.9.0 caps at
+  # ^0.39.2, and bumping it pulls in crates requiring Rust 1.88 which our nightly toolchain lacks).
+  "RUSTSEC-2026-0194",
+  "RUSTSEC-2026-0195",
 ]
 
 [licenses]
```

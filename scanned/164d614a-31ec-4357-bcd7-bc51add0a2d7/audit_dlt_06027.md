# [?] fix(docs): Fix Docusaurus build crash    (#12365)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-07-22
Source: https://github.com/iotaledger/iota/commit/07338dd7ad47e0c4959415e2027af4133a2cb0a7
Type: security-commit

## Details
fix(docs): Fix Docusaurus build crash    (#12365)

# Description of change

## Problem
The Docusaurus build crashes during compilation of the reference
documentation page for the `package_metadata` framework module.
The `try_get_modules_metadata_v1` function contains two dereference
operators, where each `*` appears immediately after a `(`.

During the docs build, docgen renders the identifiers as links with the
`<Link>` tag, so the `(*` triggering sequence becomes `(*<`. This
sequence is parsed as MDX and it acts as both an opening and a closing
emphasis delimiter, so the two `*` pair up: the text between them is
rendered into an `<em>` whose first child is a `<Link>` element.

The build's `rehype-jargon` plugin assumes every `<em>`'s first child is
plain text and calls `.toLowerCase()` on it. A `<Link>` element has no
text value, so the call throws and aborts the whole build.

## Fix

- (Root cause): Escape `*` in the framework docgen so it can never be
read as markdown emphasis.
- (Workaround): Make docusaurus aware of this pattern and add an empty
text value inside the `<em>` block, so it won't fail during the build
process

## Changes

- `crates/iota-framework/tests/build-system-packages.rs`: escape `*`
alongside `{` when emitting code blocks in `relocate_docs`.
- `docs/site/config/rehype-jargon-safe.js` (new): wrap rehype-jargon so
an `<em>` whose first child is not a text node can't crash the build.
- `docs/site/docusaurus.config.js`: use the safe wrapper.

## **Why both fixes are needed now**


_Trimmed to 38 lines — full report: https://github.com/iotaledger/iota/commit/07338dd7ad47e0c4959415e2027af4133a2cb0a7_

# [?] msggen: fix non-determinism edge case

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-05-25
Source: https://github.com/ElementsProject/lightning/commit/11b83240389128c5bf7f6342734c2465f5ee995e
Type: security-commit

## Details
msggen: fix non-determinism edge case

After adding back some fields in 62d1e3e405f722e7363d8e8dbc427039a12c421a
there is one field that was in a different place sometimes in node.proto:
DecodeInvoicePathsPath

Changelog-None

# [?] release(runway): cherry-pick chore: bump nanoid to `^3.3.17` to clear `GHSA-2v37-7h3g-55p8` (#45372)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-08-10
Source: https://github.com/MetaMask/metamask-extension/commit/c81d0a92a3394dc2a0519511eb3ed22573fdba3e
Type: security-commit

## Details
release(runway): cherry-pick chore: bump nanoid to `^3.3.17` to clear `GHSA-2v37-7h3g-55p8` (#45372)

- chore: bump nanoid to `^3.3.17` to clear `GHSA-2v37-7h3g-55p8`
cp-13.43.0 (#45362)

## **Description**

`nanoid` is a direct production dependency and `main` resolved it to
3.3.16.
[GHSA-2v37-7h3g-55p8](https://github.com/advisories/GHSA-2v37-7h3g-55p8)
covers `< 3.3.17` — a custom generator built with `customAlphabet` /
`customRandom` loops indefinitely when `size` is zero.

This moves the declared range to `^3.3.17` and consolidates every 3.x
descriptor in the tree onto a single 3.3.17 entry:

```
"nanoid@npm:^3.3.10, ^3.3.11, ^3.3.16, ^3.3.17, ^3.3.8":
  version: 3.3.17
```

Two notes for anyone repeating this, because the obvious commands both
fail in different directions:

- **`yarn dedupe` alone does not reach it.** Dedupe consolidates onto
the highest version *already in the lockfile*, so with 3.3.16 resolved
it is a no-op — the version has to be introduced with `yarn up` first.
- **A bare `yarn up nanoid` overshoots.** nanoid's `latest` dist-tag is
`6.0.1`, so it rewrites the range to `^6.0.1` and pulls a major; the 3.x
line ships under the `legacy` tag. Pinning to `@^3.3.17` keeps it in
range.

The remaining `nanoid@2.1.11` is untouched and unaffected — dev-only,
reached through `redux-devtools-core`.

## **Changelog**

CHANGELOG entry: null

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/c81d0a92a3394dc2a0519511eb3ed22573fdba3e_

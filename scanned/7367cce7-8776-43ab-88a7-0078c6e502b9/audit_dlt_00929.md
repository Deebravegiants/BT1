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

## **Related issues**

Fixes: #45334

Reachability triage for this advisory, including why the upgrade path
here is clean unlike #45325's:

https://github.com/MetaMask/metamask-extension/issues/45334#issuecomment-5241324588

## **Manual testing steps**

Dependency-only change with no runtime surface, so verification is by
resolution and audit rather than by using the app.

1. `yarn install`
2. `grep -A2 '^"nanoid@npm' yarn.lock` → every `^3.3.x` descriptor
resolves to a single `3.3.17` entry
3. `yarn npm audit --recursive --environment production` → nanoid no
longer reported

### Results on this branch

| check | result |
|---|---|
| declared range | `dependencies.nanoid` = `^3.3.17` |
| resolution | all five 3.x descriptors consolidated onto **3.3.17** |
| production audit | nanoid **not flagged** |
| diff scope | `package.json` 1 line, `yarn.lock` 10 lines |

## **Screenshots/Recordings**

N/A — no user-visible change.

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding

Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable — N/A, dependency bump
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable — N/A
- [x] I’ve applied the right labels on the PR (see [labeling

guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Patch-level dependency bump with lockfile consolidation only; no
source changes and stays on nanoid 3.x.
> 
> **Overview**
> Bumps the direct production dependency **`nanoid`** from `^3.3.8` to
**`^3.3.17`** and refreshes **`yarn.lock`** so every `^3.3.x` descriptor
resolves to a single **3.3.17** entry (replacing **3.3.16**).
> 
> This addresses

[GHSA-2v37-7h3g-55p8](https://github.com/advisories/GHSA-2v37-7h3g-55p8),
where `customAlphabet` / `customRandom` can loop indefinitely when
`size` is zero on versions below 3.3.17. There are **no application or
runtime code changes**—only dependency resolution.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
3e63d806a018e8207f378899ca4f0b07e392b151. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->
[a58c242](https://github.com/MetaMask/metamask-extension/commit/a58c2428cd64e28a4df3f22f3090f9bc982e36bc)

---------

Co-authored-by: Jongsun Suh <jongsun.suh@icloud.com>
Co-authored-by: MetaMask Bot <metamaskbot@users.noreply.github.com>

### attribution.txt
```diff
@@ -29132,7 +29132,7 @@ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLI
 ******************************
 
 nanoid
-3.3.16 <https://github.com/ai/nanoid>
+3.3.17 <https://github.com/ai/nanoid>
 The MIT License (MIT)
 
 Copyright 2017 Andrey Sitnik <andrey@sitnik.ru>
```

### package.json
```diff
@@ -537,7 +537,7 @@
     "loglevel": "^1.8.1",
     "lottie-web": "^5.12.2",
     "luxon": "^3.2.1",
-    "nanoid": "^3.3.8",
+    "nanoid": "^3.3.17",
     "pify": "^5.0.0",
     "prop-types": "^15.6.1",
     "psl": "^1.15.0",
```

### yarn.lock
```diff
@@ -33142,7 +33142,7 @@ __metadata:
     mocha: "npm:^10.2.0"
     mocha-junit-reporter: "npm:^2.2.1"
     mockttp: "npm:^4.2.3"
-    nanoid: "npm:^3.3.8"
+    nanoid: "npm:^3.3.17"
     navigator.locks: "npm:^0.8.6"
     nock: "patch:nock@npm%3A13.5.4#~/.yarn/patches/nock-npm-13.5.4-2c4f77b249.patch"
     node-fetch: "npm:^2.6.1"
@@ -33940,12 +33940,12 @@ __metadata:
   languageName: node
   linkType: hard
 
-"nanoid@npm:^3.3.10, nanoid@npm:^3.3.11, nanoid@npm:^3.3.16, nanoid@npm:^3.3.8":
-  version: 3.3.16
-  resolution: "nanoid@npm:3.3.16"
+"nanoid@npm:^3.3.10, nanoid@npm:^3.3.11, nanoid@npm:^3.3.16, nanoid@npm:^3.3.17, nanoid@npm:^3.3.8":
+  version: 3.3.17
+  resolution: "nanoid@npm:3.3.17"
   bin:
     nanoid: bin/nanoid.cjs
-  checksum: 10/8004af92b5541af1dbd23b69845b5026f777d5b7ef07163cea1837aae86e052ced8b383cecbf8a4f1b5e77ae207df96dc45e16b9e0fa3c4b761d085f1e42851b
+  checksum: 10/54c3238ba6ea31c173ccf70922481814892075dbf1b4636abec249d0b34d5594fc9a8892c04872068674010a11fa3d18316dc06e59e700def131ff9d8e740426
   languageName: node
   linkType: hard
 
```

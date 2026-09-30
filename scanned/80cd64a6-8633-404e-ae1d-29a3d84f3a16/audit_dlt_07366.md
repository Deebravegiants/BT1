# [?] chore: ignore minimatch ReDoS advisory (GHSA-3ppc-4f35-3m26) (#40221)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-19
Source: https://github.com/MetaMask/metamask-extension/commit/2d9725edb6501db7c413b13f219b6ff510eaa326
Type: security-commit

## Details
chore: ignore minimatch ReDoS advisory (GHSA-3ppc-4f35-3m26) (#40221)

## **Description**

Adds minimatch advisory
[GHSA-3ppc-4f35-3m26](https://github.com/advisories/GHSA-3ppc-4f35-3m26)
(ID 1113296) to `npmAuditIgnoreAdvisories` in `.yarnrc.yml`.

**Reason:** minimatch <10.2.1 has a high-severity ReDoS vulnerability
via repeated wildcards with non-matching literals.

**Why ignore:** The vulnerable versions (3.1.2 via `eslint-plugin-n`,
10.1.1 via `glob`) are only used in dev/build-time dependencies and are
not shipped to users.

## **Changelog**

CHANGELOG entry: null

## **Related issues**

Fixes:

## **Manual testing steps**

1. Run `yarn npm audit` and verify advisory 1113296 no longer appears.

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I’ve applied the right labels on the PR (see [labeling
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
> Config-only change that affects audit reporting/CI noise, not runtime
behavior. Risk is mainly that a real vulnerability could be overlooked
if `minimatch` usage changes in the future.
> 
> **Overview**
> Updates `.yarnrc.yml` to ignore npm audit advisory `1113296` for
`minimatch` (GHSA-3ppc-4f35-3m26), with comments documenting that the
ReDoS issue is only present in dev/build-time dependencies and not
shipped to users.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
be18b6e8929c97e7aa383ccddd346c3d43a8f843. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### .yarnrc.yml
```diff
@@ -43,6 +43,11 @@ npmAuditIgnoreAdvisories:
   # URL: https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
   - 1113214
 
+  # Issue: minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern
+  # Only affects dev/build-time dependencies (eslint-plugin-n, glob) — not shipped to users.
+  # URL: https://github.com/advisories/GHSA-3ppc-4f35-3m26
+  - 1113296
+
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
```

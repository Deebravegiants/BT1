# [?] fix: bump `fast-xml-parser` to `5.3.6` to fix DoS vulnerability and ignore `ajv` advisory (#40187)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-18
Source: https://github.com/MetaMask/metamask-extension/commit/a6f0d07f373c23a0ba8912ce2ecd1fc26e15d68d
Type: security-commit

## Details
fix: bump `fast-xml-parser` to `5.3.6` to fix DoS vulnerability and ignore `ajv` advisory (#40187)

## **Description**

Bumps the
[`fast-xml-parser`](https://github.com/NaturalIntelligence/fast-xml-parser/blob/master/CHANGELOG.md)
yarn resolution from `^5.3.4` to `^5.3.6` to resolve a high-severity DoS
vulnerability caused by unrestricted entity expansion in DOCTYPE
parsing.

- **Reason:** `fast-xml-parser` versions `>=4.1.3 <5.3.6` are affected
by
[GHSA-jmr7-xgp7-cmfj](https://github.com/advisories/GHSA-jmr7-xgp7-cmfj).
- **Solution:** Bump the resolution override to `^5.3.6`, the first
patched version. The vulnerable dependency is pulled in transitively via
`@metamask/snaps-utils@12.1.0`.

Also ignores `ajv` advisory since it does not impact production and is
hard to update.

## **Changelog**

CHANGELOG entry: null

## **Related issues**

Fixes: https://github.com/advisories/GHSA-jmr7-xgp7-cmfj

## **Manual testing steps**

1. Run `yarn audit` and verify `fast-xml-parser` and `ajv` no longer
appears as vulnerable.
2. Run `yarn install` and confirm no resolution errors.

## **Screenshots/Recordings**

### **Before**


_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/a6f0d07f373c23a0ba8912ce2ecd1fc26e15d68d_

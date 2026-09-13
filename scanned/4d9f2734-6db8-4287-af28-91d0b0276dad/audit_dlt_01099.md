# [H] OpenZeppelin Contracts Wizard has Code Injection in Generated Hardhat and Foundry Tests via Unsanitized opts.name / opts.uri

## Summary
Severity: High
Chain: @openzeppelin/wizard
Component: @openzeppelin/wizard
CVE: CVE-2026-48054
CWE: Improper Control of Generation of Code ('Code Injection')
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-4x76-22x2-rx8v
Type: github-advisory

## Details
## Summary

The OpenZeppelin Contracts Wizard generated Hardhat (`test/test.ts`) and Foundry (`test/<Name>.t.sol`) example test files that interpolated user-supplied strings (`opts.name`, `opts.uri`) into the test source without escaping. A crafted input could produce a generated test file in which the input string broke out of its surrounding literal and was parsed as code, executing when a developer ran `npm test` or `forge test` on the downloaded project.

## Impact

- **Users of the hosted Wizard at https://wizard.openzeppelin.com:** no action required. The site has been redeployed with the fix.
- **Users of `@openzeppelin/wizard` via the documented public API:** not affected. The vulnerable functions (`zipHardhat`, `zipFoundry`) are not part of the package's documented public exports.
- **Callers of `zipHardhat` / `zipFoundry` who forward externally-controlled strings into `opts.name` / `opts.uri`:** upgrade to `0.10.9`.

## Patches

Fixed in `@openzeppelin/wizard@0.10.9`.

# [C] Not backed by any physical asset

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
USD token is what is called a “fiat” currency. Fiat money is an intrinsically worthless object, that is deemed to be money by law (in this case, US law). This means that users of USD token are required to trust the US government to exist and operate correctly in order to use it. A black-swan scenario where the US government ceases to exist and enforce the USD token’s value would cause a global financial crisis.

Consider reverting to the [gold standard](https://en.wikipedia.org/wiki/Gold%5Fstandard) and having each USD token represent a fixed amount of gold.

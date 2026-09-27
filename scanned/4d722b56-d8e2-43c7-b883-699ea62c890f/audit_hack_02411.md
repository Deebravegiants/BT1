# [M] Fail early and loudly

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
In the spirit of [failing as promptly as possible](https://oncodingstyle.blogspot.com.ar/2008/10/fail-early-fail-loudly.html) in all methods, consider adding checks in functions `allocatePresaleBalances`,`allocateSaleBalances`, and`allocateLockedBalances`of **ParticipantAdditionProxy** to ensure that both arrays passed in as parameters have the same length. If the first array passed in is shorter than the second by mistake (ie if an address is missing for an allocation), then the code will silently continue.

**Update**: _Fixed in [this](https://github.com/unikoingold/UnikoinGold-UKG-Contract/commit/1d7cd26bbd4a1cfd0ce99a47d1337490df524618) commit._

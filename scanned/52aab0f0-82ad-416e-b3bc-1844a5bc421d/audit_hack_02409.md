# [M] Unchecked math operations

## Summary
Severity: Medium
Source: https://github.com/qiibee/qb-contracts/blob/d40368c9a7a536572a5bb03cb031d658ccb34f24/contracts/QiibeeToken.sol#L114
Type: audit-issue

## Details
There are three unchecked math operations inside the migration function in lines [114](https://github.com/qiibee/qb-contracts/blob/d40368c9a7a536572a5bb03cb031d658ccb34f24/contracts/QiibeeToken.sol#L114)–[116](https://github.com/qiibee/qb-contracts/blob/d40368c9a7a536572a5bb03cb031d658ccb34f24/contracts/QiibeeToken.sol#L116) . It’s always better to be safe and perform operations with correctness assertions.

Consider rigorously checking for under and overflows for all of the arithmetic operations. We recommend using the [SafeMath](https://github.com/OpenSTFoundation/SimpleTokenSale/blob/1a1e863441ba0149d7585203f5dbc6e800af00cf/contracts/SafeMath.sol) library from OpenZeppelin.

_**Update:** Fixed in [this](https://github.com/qiibee/qb-contracts/commit/25efdbf5bc29de12a724450c540218f6c8e59129) commit._

# [M] 5.3.7 Initial depositor can inflate share to siphon yield of smaller deposits

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** WETHRebasing.sol#L53-L

**Description:** The initial_totalSharesof 1 is insufficient to guard against a share inflation attack that affects yield
accrual.

Using the intended config ofprice() = 1e9(1 gwei), an initial depositor can:

- Deposit 1 share of 1 gwei.
- Create a contract thatselfdestruct()to forcibly send ETH to the contract to inflate_sharePrice(), e.g. 1
    ETH.
- _sharePrice()becomes(1e18 + 2e9) / 2=0.500000001ETH.


# DRAFT

Because yield doesn't get distributed to remainders, this will prevent small deposits and remainders of <= 0.5 ETH
from receiving yield, which is distributed amongst those with shares (>= 0.500000001 ETH), although in the case
above, the attacker loses 0.5 ETH as a trade-off.

**Recommendation:** Increase the initial_totalSharesto a larger number like 1000 , which is what UniswapV2 uses.

# [C] 6.1 Anyone Can Disable TUSD Market

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

The TrueUSD (TUSD) token has two addresses through which it can be called. Calling the transfer
function on either address affects the balance of both addresses. Given that there is a Compound market
for TUSD, it is important to note that anyone can disable this market by calling:

```
function sweepToken(EIP20NonStandardInterface token) override external {
require(address(token) != underlying, "CErc20::sweepToken: can not sweep underlying token");
uint256 balance = token.balanceOf(address(this));
token.transfer(admin, balance);
}
```
Usually, this function is meant to collect stray tokens and send them back to the admin. However, in this
case anyone can call this with the second address of TUSD and thereby transfer all TUSD inside the
market to the administrator.

The funds are not lost, as they reside with the administrator, but no more borrows or redemptions will be
possible. However, this causes a sudden change in the exchange rate and the interest rate of the token,
which are both calculated using the current balance of the contract.

The dropped exchange rate allows different attacks. Among other things, it allows:

- liquidation of users who used cTUSD as collateral (if the collateral factor is bigger than 0)
- borrowing TUSD, then executing the attack and paying back less TUSD
- executing the attack, minting cTUSD, waiting for the exchange rate to be restored and redeeming
    cTUSD for more TUSD than were used for minting


Code corrected:

The sweepToken function can now only be called by the admin.

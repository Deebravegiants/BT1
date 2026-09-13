# [M] 5.1 CRV Not Locked When Used to Mint YCRV

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Risk Accepted

When YCRV is minted with the mint() function, CRV is not locked.

In yveCRV, CRV is locked upon minting. In YCRV.mint(...) it is not locked immediately, but a separate
call to StrategyProxy.lock() is needed.

```
assert ERC20(CRV).transferFrom(msg.sender, VOTER, amount) # dev: no allowance
self._mint(_recipient, amount)
log Mint(msg.sender, _recipient, False, amount)
return amount
```
Not locking the CRV immediately in the CRV voting escrow implies a mismatch between the total supply
of YCRV and the effective voting power and total rewards of VOTER. It also imposes increased trust
requirements towards governance, which might sweep the not yet locked CRV from the VOTER.

Risk accepted

Yearn states:

```
Locking CRV is gas intensive. Decision was made to have locking occur at
some periodic interval via external process rather than burden each user
with gas costs.
```

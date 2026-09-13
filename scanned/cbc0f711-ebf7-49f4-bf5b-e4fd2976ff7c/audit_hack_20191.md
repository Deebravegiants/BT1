# [H] 6.2.3 _hasFundableKeysmarks operators that have no more fundable validators as fundable.

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** Operators.sol#L151-L

**Description:** Sinceoperator.keys >= operator.limit(based on the checks whenoperator.keyshas been
set), we can simplify_hasFundableKeys'sreturnexpression to:

```
operator.active && operator.limit > (operator.funded - operator.stopped)
```
Also based on the assumption atNon-zerooperator.limitshould always be greater than or equal toopera-
tor.funded, if true:

```
operator.limit >= operator.funded
```
This means an active operator that has at least one stopped validator would pass the test
(_hasFundableKeys(operator) == true)

```
(stop, funded, limit, keys) = (s, F, L, K) // where s > 0
```
Even operators that have theirfundedequal to theirlimit:

```
(stop, funded, limit, keys) = (s, F, F, K)// where s > 0
```
Although they are maxed out for further funding. For these cases_hasFundableKeysreturnstrue. So based on
these findings it would make sense to have this function return:

```
operator.active && ( operator.limit > operator.funded )
```
Unless some other changes are applied toOperatorResgistry.1.sol, specially its_getNextValidatorsFromAc-
tiveOperatorsfunction.

Also, note thatfunded,limit, andkeysare not only counters for theoperator's struct, but also they define ranges
inValidatorKeysfor theoperator(based on the way that they have been used inOperatorResgistry.1.sol).
And this is one of the main differences between these 3 fields and thestoppedfield. Thestoppedfield is only
used as a counter.

**Alluvial:** Exactly! We shouldn't takestoppedinto account for the_hasFundableKeys, but we should keep it in the
optimal operator search as we want to favor operators with the lowest count of running validators.

**Spearbit:** So basicallystoppedis used for maybe bookkeeping off-chain and also for the optimal search algorithm
for picking the next validators.

**Alluvial:** Yes, currently it's more like a manual feature because exits should be rare but it will be a core part of
the process once withdrawals are here and operators will often have to exit validators for users to redeemETH.
Recommendation implemented in SPEARBIT/3.

**Spearbit:** Acknowledged.

# [M] 6.7 Trust Model of External Adapters

## Summary
Severity: Medium
Source: https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed Code Corrected

The trust model for the external adapters has not been properly specified. Moreover, all four available
adapters behave differently and the assumptions these adapters rely on have not been documented.

After the action on the external system which is invoked by an adapter, there is a check on the collateral
of the credit account. All currently available adapters use the following function which takes the following
parameters:


```
function checkCollateralChange(
address creditAccount,
address tokenIn,
address tokenOut,
uint256 amountIn,
uint256 amountOut
)
```
The concern is about what is passed as amount especially for the spent asset. It is vital that these
amounts represent the actual state of the credit accounts holding or the check may be circumvented.

Some adapters rely on the values returned by the 3rd party system, some query the actual balance.

While querying the actual balance for the assets involved in the action is the safest option, it may be
expensive in terms of gas. However note that in the current implementation of the EVM (London
hardfork), repeated access to the same contract/storage location got significantly cheaper the overhead
in terms of gas may not be that big.

Using values returned by the call to the third-party contract may be an option if the third-party contract is
fully trusted to do so correctly. Similarly, this holds for input parameters. This critical part should be
documented and assessed thoroughly. In case of doubts/uncertainties, it may be safer to query the
balances and calculate the delta of the balances and use this.

Regarding the YearnAdapter, it can be inspected and documented: Querying the balances could be
avoided since both Vault.deposit and Vault.withdraw
[https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy] return the change in the balance of
the tokens of interest. However, the current YearnAdapter does not do this but queries the balance and
calculates the delta.

The UniswapV3 Adapter relies on the returned values by the 3rd party system. However, there is no
documentation why this assumption holds.

Specification changed and code corrected:

A pattern of how all adapters should be built has been created. All existing adapters have been rewritten
to adhere to this pattern: The balance is queried before and after the action and the difference is used for
the check of the collateral change.

Note that due to the existing token allowances for the adapters from the credit accounts these checks are
not 100% failsafe. It is vital that the 3rd party system is fully trusted to not transfer any other tokens of the
credit account. The system performs the fast check only for the tokens passed as arguments to the
check. Any other change in balance will be ignored.

# [M] Mitigation of M-02: Issue perhaps NOT sufficiently mitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/63
Type: code-finding

## Details
# Mitigation of M-02: Issue perhaps NOT sufficiently mitigated

## Mitigated issue
[M-02: sFrxEth may revert on redeeming non-zero amount](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/1049)

The issue was that `SfrxEth.withdraw(_amount)` may revert when called in `unstake()`, blocking unstaking, if `_amount` is low (most realistically if `_amount == 1`).

## Mitigation review
The issue has been attempted to be mitigated by introducing the possibility to enable and disable derivatives. This allows for `SfrxEth` to be disabled when it is expected that `SfrxEth.withdraw(1)` would be called under the circumstance that it would revert.

When disabling `SfrxEth` its remaining balance is effectively forgone. In order for `unstake()` to call `SfrxEth.withdraw(1)` we would need that `1 == (derivatives[i].balance() * _safEthAmount) / safEthTotalSupply`. Assuming the protocol would be willing to forgo up to x wei to close down `SfrxEth` then the user can towards this point only unstake at least an x-th of the supply of SafEth. As a comparison consider the total market value of Ethereum which has been up to over $500B. A 1e12-th of this is $0.5. 1e12 wei is a very small amount to sacrifice, and a user will perhaps not be too upset over not being able to unstake $0.5 until the owner has disabled `SfrxEth`.

Thus the issue is perhaps sufficiently mitigated in practice for the individual user or EOA.

However, other contracts interacting with `SafEth` may operate differently. They might, for example, depend on occasionally being able to unstake very small amounts, or else have their functionality impeded or blocked.
I imagine the protocol would be less happy to forgo 1e18 wei if it could be avoided. Then we have an issue if it should be possible to unstake 1e18-th of the total supply.
It is therefore in the interface with other contracts that I think this might still be an issue.

The main takeaway here is that M-02 is an issue not only when the balance of `SfrxEth` is `1` but at significantly higher balances than that (such as 1e12 or 1e18 in the examples above), and technically at any balance.
In this sense the issue is not resolved.

### Conclusion
In order to resolve this issue without the risk of having to sacrifice funds `SfrxEth` must be bypassed on a call by call basis. The issue presents only when `_amount` is small, so it doesn't matter much if the call is skipped in that case. The best fix is to explicitly check if `IsFrxEth(SFRX_ETH_ADDRESS).previewRedeem(_amount) == 0` and skip the call in that case only. In that case no ether would have been returned anyway, so nothing is lost.

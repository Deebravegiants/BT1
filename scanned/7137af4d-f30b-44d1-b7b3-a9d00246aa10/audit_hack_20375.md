# [H] 5.2.2 commitYieldReport()will revert when withdrawing insurance to cover negative yield

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** YieldManager.sol#L264-L265, DSRYieldProvider.sol#L74-L

**Description:** commitYieldReport()callscommitYield()on the provider to determine how much yield was gained
since the last call:

```
// Commit the yield for the provider
int256 committedYield = YieldProvider(_providers.at(i)).commitYield();
```
This returnsyield(), which is calculated asstakedValue() - stakedBalance, as seen below:

```
function yield() public view override returns (int256) {
return int256(stakedValue()) - int256(stakedBalance);
}
```
However,committedYieldwill still be negative forDSRYieldProviderafter funds are withdrawn from insurance to
cover losses.

The issue is thatDSRYieldProviderunstakes and holds DAI in the insurance contract. As such, whenwith-
drawFromInsurance()is called to cover the loss, it transfers DAI to theYieldManager.

ForDSRYieldProvider,stakedValue()won't increase afterwithdrawFromInsurance()as the withdrawn DAI
remains unstaked, socommittedYieldwon't change.

This will causecommitYieldReport()to revert in the sanity check below.

**Recommendation:** In withdrawFromInsurance(), consider staking the withdrawn DAI using
DSR_MANAGER.join().

Additionally, add a//@devcomment inwithdrawFromInsurance()that it should ensure that withdrawn funds
increasestakedValue(), ie. they should be staked.


```
DRAFT
```

# [M] A single external protocol can DOS rebalanc-

## Summary
Severity: Medium
Contest weight: 0.5954
Dataset id: 20000
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A single external protocol can DOS the entire rebalance process in Notional.
acts/external/pCash/ProportionalRebalancingStrategy.sol#L23
File: ProportionalRebalancingStrategy.sol
```solidity
function calculateRebalance(
    IPrimeCashHoldingsOracle oracle,
    uint8[] calldata rebalancingTargets
) external view override onlyNotional returns (RebalancingData memory rebalancingData) {
    address[] memory holdings = oracle.holdings();
..SNIP..
    for (uint256 i; i < holdings.length;) {
        address holding = holdings[i];
        uint256 targetAmount = totalValue * rebalancingTargets[i] / uint256(Constants.PERCENTAGE_DECIMALS);
        uint256 currentAmount = values[i];

        redeemHoldings[i] = holding;
        depositHoldings[i] = holding;
..SNIP..
    }
    rebalancingData.redeemData = oracle.getRedemptionCalldataForRebalancing(redeemHoldings, redeemAmounts);
    rebalancingData.depositData = oracle.getDepositCalldataForRebalancing(depositHoldings, depositAmounts);
}
```
During a rebalance, the ProportionalRebalancingStrategy will loop through all the holdings and perform a deposit or redemption against the external market of the holdings.
Assume that Notional integrates with four (4) external money markets (Aave V2, Aave V3, Compound V3, Morpho). In this case, whenever a rebalance is executed, Notional will interact with all four external money markets.
acts/external/actions/TreasuryAction.sol#L304
File: TreasuryAction.sol
```solidity
function _executeDeposits(Token memory underlyingToken, DepositData[] memory deposits) private {
..SNIP..
    for (uint256 j; j < depositData.targets.length; ++j) {
        // This will revert if the individual call reverts.
        GenericToken.executeLowLevelCall(
            depositData.targets[j],
            depositData.msgValue[j],
            depositData.callData[j]
        );
    }
}
```
acts/internal/balances/TokenHandler.sol#L357
File: TokenHandler.sol
```solidity
function executeMoneyMarketRedemptions(
..SNIP..
    for (uint256 j; j < data.targets.length; j++) {
        // This will revert if the individual call reverts.
        GenericToken.executeLowLevelCall(data.targets[j], 0, data.callData[j]);
    }
```
However, as long as one external money market reverts, the entire rebalance process will be reverted and Notional would not be able to rebalance its underlying assets.
The call to the external money market can revert due to many reasons, which include the following:
• Changes in the external protocol's interfaces (e.g. function signatures modified or functions added or removed)
• The external protocol is paused
• The external protocol has been compromised
• The external protocol suffers from an upgrade failure causing an error in the new contract code.
Notional would not be able to rebalance its underlying holding if one of the external money markets causes a revert. The probability of this issue occurring increases whenever Notional integrates with a new external money market
The key feature of Notional V3 is to allow its Treasury Manager to rebalance underlying holdings into various other money market protocols.
This makes Notional more resilient to issues in external protocols and future-proofs the protocol. If rebalancing does not work, Notional will be unable to move its fund out of a vulnerable external market, potentially draining protocol funds if this is not
Another purpose of rebalancing is to allow Notional to allocate Notional V3’s capital to new opportunities or protocols that provide a good return. If rebalancing does not work, the protocol and its users will lose out on the gain from the investment.
On the other hand, if an external monkey market that Notional invested in is consistently underperforming or yielding negative returns, Notional will perform a rebalance to reallocate its funds to a better market. However, if rebalancing does not work, they will be stuck with a suboptimal asset allocation, and the protocol and its users will incur losses.

## Recommendation
Consider implementing a more resilient rebalancing process that allows for failures in individual external money markets. For instance, Notional could catch reverts from individual money markets and continue the rebalancing process with the remaining markets.

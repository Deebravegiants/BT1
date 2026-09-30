# [H] Incorrect Claiming Logic in RebateDistributor::claimAdminRebates()

## Summary
Severity: High
Contest weight: 0.7876
Dataset id: 12397
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LineaBank protocol, the RebateDistributor contract provides functions for the keeper to claim admin rebates and the users to claim users rebates. While reviewing the rebate-claiming logic, we notice it calls a wrong internal routine to claim the admin rebates, and the claimed market fees are locked in the contract.
To elaborate, we show below the related code snippets of the claimAdminRebates()/accruedAdminRebate routines. As the name indicates, the first one is used by the keeper to claim the admin rebates.
Our analysis shows that it calls the RebateDistributor::accruedRebates() routine (line 162) to calculate the rebates for the admin, which is designed to calculate the rebates for normal users. As a result, it claims wrong rebates for the admin. To fix, it needs to call the RebateDistributor::accruedAdminRebate() routine to calculate the rebates for the admin.
Moreover, in the RebateDistributor::claimAdminRebates() routine, it updates the timestamp of the last claimed check point for the user (line 164), i.e., userCheckpoint[msg.sender]. Our analysis shows that it should update the timestamp of the last claimed check point for the admin, i.e., adminCheckpoint.
Public
```solidity
function claimAdminRebates()
    external
    override
    nonReentrant
    onlyKeeper
    returns (
        uint256 addtionalLabAmount,
        uint256[] memory marketFees
    )
{
    (, addtionalLabAmount, marketFees) = accruedRebates(msg.sender);
    Constant.RebateCheckpoint memory lastCheckpoint = rebateCheckpoints[
        rebateCheckpoints.length - 1
    ];
    userCheckpoint[msg.sender] = _truncateTimestamp(lastCheckpoint.timestamp.sub(REBATE_CYCLE));
    address(lab).safeTransfer(msg.sender, addtionalLabAmount);
}

function accruedAdminRebate() public view returns (
    uint256 additionalLabAmount,
    uint256[] memory marketFees
) {
    Constant.RebateCheckpoint memory lastCheckpoint = rebateCheckpoints[
        rebateCheckpoints.length - 1
    ];
    address[] memory markets = core.allMarkets();
    marketFees = new uint256[](markets.length);
    for (
        uint256 nextTimestamp = _truncateTimestamp(adminCheckpoint).add(REBATE_CYCLE);
        nextTimestamp <= lastCheckpoint.timestamp.sub(REBATE_CYCLE);
        nextTimestamp = nextTimestamp.add(REBATE_CYCLE)
    ) {
        uint256 checkpointIdx = _getCheckpointIdxAt(nextTimestamp);
        Constant.RebateCheckpoint storage currentCheckpoint = rebateCheckpoints[
            checkpointIdx
        ];
        additionalLabAmount = additionalLabAmount.add(
            currentCheckpoint.additionalLabAmount.mul(currentCheckpoint.adminFeeRate).div(1e18)
        );
        for (uint256 i = 0; i < markets.length; i++) {
            if (currentCheckpoint.marketFees[markets[i]] > 0) {
                marketFees[i] = marketFees[i].add(
                    currentCheckpoint.marketFees[markets[i]].mul(currentCheckpoint.adminFeeRate)
                        .div(1e18)
                );
            }
        }
    }
    return (additionalLabAmount, marketFees);
```
What's more, the rebates are composed of LAB and market fees. The market fees are pulled into the contract via the RebateDistributor::addMarketUTokenToRebatePool() routine (as the code shown below). However, in the RebateDistributor::claimAdminRebates() routine, we notice it only transfers the rebates of LAB to the caller, the rebates of market fees are not transferred to the caller. As a result, the market fees are locked in the contract.
Note the same issue is also applicable to the RebateDistributor::claimRebates() routine, where the claimed market fees are not transferred to the user.
```solidity
function addMarketUTokenToRebatePool(address lToken, uint256 uAmount) external payable override nonReentrant {
    Constant.RebateCheckpoint storage lastCheckpoint = rebateCheckpoints[
        rebateCheckpoints.length - 1
    ];
    address underlying = ILToken(lToken).underlying();
    if (underlying == ETH && msg.value > 0) {
        lastCheckpoint.marketFees[lToken] = lastCheckpoint.marketFees[lToken].add(msg.value);
    } else if (underlying != ETH) {
        address(underlying).safeTransferFrom(msg.sender, address(this), uAmount);
        lastCheckpoint.marketFees[lToken] = lastCheckpoint.marketFees[lToken].add(uAmount);
    }
```
Public

## Recommendation
Revisit the RebateDistributor::claimAdminRebates() routine to call the RebateDistributor::accruedAdminRebate() routine to calculate the rebates for the admin and properly transfer the market fees to the caller.

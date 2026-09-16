### Title
`UniV3UniswapV2Wrapper.swapExactTokensForETH` decodes the router's reported `amountOut` instead of measuring actual WETH received, causing a revert-on-withdraw DoS - (File: evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol)

### Summary
`swapExactTokensForETH` trusts the `amountOut` value returned by the Uniswap V3 `SwapRouter02.exactInputSingle` call (via `abi.decode`) and immediately calls `IWETH(weth).withdraw(amountOut)` on that value, rather than measuring the wrapper's actual WETH balance increase. This is the same bug class as the `RewardHandler.sellRewards` finding: an external swap's self-reported output accounting is used to drive a subsequent balance-consuming operation (`safeTransfer` in the original; `IWETH.withdraw` here), and any discrepancy between the router's reported value and the wrapper's real WETH balance change causes a revert, denying service to whoever relies on this swap path.

### Finding Description
In `swapExactTokensForETH`:
```solidity
bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
uint256 amountOut = abi.decode(results[0], (uint256));

IWETH(weth).withdraw(amountOut);
(bool sent,) = to.call{value: amountOut}("");
``` [1](#0-0) 

`amountOut` here is the value the Uniswap V3 router self-reports as the result of `exactInputSingle`, not a measured balance delta of the wrapper contract. This mirrors the audited flaw in `RewardHandler.sellRewards`, where `amountOut` decoded from the ODOS router's return data was used for `safeTransfer` instead of the actual `balanceOf` delta, causing reverts whenever the router under- or mis-reports the true amount transferred.

Contrast this with the sibling contract `UniV4UniswapV2Wrapper.swapExactTokensForETH`, which correctly measures the actual native balance delta instead of trusting a decoded return value:
```solidity
uint256 balanceBefore = to.balance;
IUniversalRouter(_params.universalRouter).execute(...);
amounts[1] = to.balance - balanceBefore;
``` [2](#0-1) 

This shows the codebase is aware of, and elsewhere applies, the "measure actual balance change" mitigation pattern (also used pervasively in `IntentGatewayV2.sol`'s fee-on-transfer handling, e.g. `received = IERC20(token).balanceOf(address(this)) - balBefore;`) [3](#0-2)  — but `UniV3UniswapV2Wrapper.swapExactTokensForETH` was not updated to follow it, leaving the ODOS-class bug present specifically in the V3 wrapper's `withdraw(amountOut)` step.

If the wrapper's actual WETH balance increase after the V3 swap is less than the router-reported `amountOut` (for example, because the input token behaves atypically on transfer, because of multicall/quoter or accounting edge cases in the V3 router path, or any other discrepancy between the router's internal ledger and the wrapper's real token balance), `IWETH(weth).withdraw(amountOut)` will revert because the wrapper does not actually hold enough WETH to unwrap that amount.

### Impact Explanation
A revert in `swapExactTokensForETH` denies service to any caller/integration routing token→ETH swaps through this wrapper (e.g., as a `predispatch`/`postdispatch` swap venue for `IntentGatewayV2` cross-chain/same-chain intents, as used elsewhere in the repo's swap-wrapper tests and deployment scripts). Any transaction depending on this function to convert escrowed/solver tokens into ETH will unconditionally revert, causing denial of service for that swap leg — the same "managed funds revert" class of impact identified in the original report, applied here to a Hyperbridge intents/swap-routing component reachable by ordinary unprivileged callers (solvers, fillers, or order predispatch/postdispatch calldata).

### Likelihood Explanation
The likelihood is Medium: the discrepancy does not require malicious governance/collator or protocol-level exploitation — it can be triggered by any token/pool combination where the V3 router's self-reported `amountOut` doesn't exactly match the wrapper's realized WETH balance increase, or by any pool/token idiosyncrasy the router does not perfectly account for on the recipient contract. This is a lower-probability trigger than a directly manipulable input, but it is a real class of bug (as proven by the analogous ODOS finding) rather than a purely theoretical one, and it requires no special privilege to reach — only calling `swapExactTokensForETH` with an eligible token/path.

### Recommendation
Compute `amountOut` from the wrapper's own measured WETH balance delta rather than from the router's decoded return value, mirroring the fix already applied in `UniV4UniswapV2Wrapper` and in `IntentGatewayV2`'s fee-on-transfer handling:
```solidity
uint256 balanceBefore = IERC20(weth).balanceOf(address(this));
bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
uint256 amountOut = IERC20(weth).balanceOf(address(this)) - balanceBefore;

IWETH(weth).withdraw(amountOut);
(bool sent,) = to.call{value: amountOut}("");
if (!sent) revert RefundFailed();
```
This ensures `withdraw` is always called with an amount the contract actually holds, eliminating the DoS vector.

### Proof of Concept
A concrete PoC (mock V3 router that returns an `amountOut` value larger than the WETH it actually transfers to the wrapper, analogous to `CyfrinMockOdosRouter.swapSkewed` in the reference report) would demonstrate:
1. Deploy a mock `IV3SwapRouter`/`IMulticallExtended` that, for `exactInputSingle`, transfers `X` WETH to the wrapper but returns `amountOut = Y > X` in its encoded result.
2. Call `UniV3UniswapV2Wrapper.swapExactTokensForETH(amountIn, amountOutMin, path, to, deadline)`.
3. Observe the call reverts inside `IWETH(weth).withdraw(amountOut)` because the wrapper's actual WETH balance (`X`) is less than the decoded `amountOut` (`Y`), reproducing the same "receive less than expected" DoS documented for `RewardHandler.sellRewards`.

Full exploit wiring (mock router deployment, `vm.etch`, exact assertions) would need to be built out by an engineer with test-suite access, following the pattern of `test_cyfrin_SellRewards_RevertWhen_AmountOutOverstatesManagedIncrease` in the reference report and the existing `UniV3UniswapV2WrapperTest.sol` test harness in this repo.

### Citations

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L196-201)
```text
        bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
        uint256 amountOut = abi.decode(results[0], (uint256));

        IWETH(weth).withdraw(amountOut);
        (bool sent,) = to.call{value: amountOut}("");
        if (!sent) revert RefundFailed();
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L128-136)
```text
        uint256 balanceBefore = to.balance;

        IUniversalRouter(_params.universalRouter).execute(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = to.balance - balanceBefore;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L320-322)
```text
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
```

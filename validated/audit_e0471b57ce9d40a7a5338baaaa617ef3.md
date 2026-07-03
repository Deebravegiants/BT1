Audit Report

## Title
Ineffective ETH Deposit Limit Check Allows Depositors to Exceed Protocol Cap - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` omits the incoming `amount` from the ETH branch comparison, making the cap check ineffective. While the ERC20 branch correctly evaluates `totalAssetDeposits + amount > depositLimit`, the ETH branch evaluates only `totalAssetDeposits > depositLimit`. Any depositor can push ETH deposits arbitrarily above the configured cap as long as the total has not already exceeded it at the time of the call.

## Finding Description
At lines 676–682 of `contracts/LRTDepositPool.sol`, the function `_checkIfDepositAmountExceedesCurrentLimit` contains an asymmetric guard:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));  // amount omitted
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));  // correct
}
``` [1](#0-0) 

The ETH branch never returns `true` while `totalAssetDeposits <= depositLimit`, regardless of how large `amount` is. This means the guard at lines 661–663, which calls this function and reverts on `true`, never fires for ETH deposits that would push the total over the cap — only for deposits made after the cap is already breached. [2](#0-1) 

The call chain is: `depositETH` (L76–93) → `_beforeDeposit` (L648–670) → `_checkIfDepositAmountExceedesCurrentLimit`. The `depositETH` function is public and permissionless. [3](#0-2) 

## Impact Explanation
The ETH deposit cap configured via `lrtConfig.depositLimitByAsset(ETH)` is not enforced. Any depositor can mint rsETH beyond the protocol's intended ceiling. The protocol fails to deliver its promised deposit limit invariant. No funds are directly stolen or frozen; the contract simply mints more rsETH than the cap allows.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

## Likelihood Explanation
`depositETH` is a public, payable, permissionless function. No special role, flash loan, or external dependency is required. The exploitable condition (`totalAssetDeposits <= depositLimit`) is the normal operating state of the protocol. Any user can trigger this at any time before the cap is already breached, and the overshoot is unbounded per call and repeatable across blocks.

**Likelihood: High.**

## Recommendation
Add `amount` to the ETH branch to match the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

## Proof of Concept
1. Deploy/fork with `depositLimitByAsset(ETH) = 1000 ether` and `getTotalAssetDeposits(ETH) = 999 ether`.
2. Call `depositETH{value: 500 ether}(0, "")` from any EOA.
3. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 500 ether)` evaluates `999 ether > 1000 ether` → `false`.
4. `_beforeDeposit` does not revert; rsETH is minted for 500 ETH.
5. `getTotalAssetDeposits(ETH)` is now `1499 ether`, ~50% above the cap.
6. The call can be repeated by any depositor with no bound on overshoot.

**Foundry test plan:** Write an invariant test asserting `getTotalAssetDeposits(ETH) <= lrtConfig.depositLimitByAsset(ETH)` after any sequence of `depositETH` calls. The invariant will be broken by the fuzzer with a single deposit call when the pre-deposit total is at or near the cap.

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```

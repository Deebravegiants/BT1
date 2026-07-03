Audit Report

## Title
Excess ETH Permanently Locked in `MultiChainRateProvider` Due to Missing Recovery Mechanism - (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`MultiChainRateProvider.updateRate()` is a public `payable` function that forwards exactly `estimatedFee` per registered receiver to LayerZero, but has no mechanism to return or recover any `msg.value` in excess of the total fees consumed. Because the contract inherits only `Ownable` and `ReentrancyGuard` with no `recoverETH()` or `receive()` sweep, any residual ETH is permanently locked. Both production deployments — `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` — inherit this same gap.

## Finding Description
`MultiChainRateProvider` is declared as:

```solidity
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
``` [1](#0-0) 

`updateRate()` iterates over all `rateReceivers`, calls `estimateFees` on-chain for each, and forwards exactly that amount to the LayerZero endpoint:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
``` [2](#0-1) 

The refund address passed to LayerZero is `payable(msg.sender)`, so any LayerZero-side refund goes to the caller — but ETH that was never forwarded to LayerZero (i.e., `msg.value − Σ estimatedFee_i`) simply remains in `address(this).balance`. No function in `MultiChainRateProvider` or either concrete subcontract touches this balance:

- No `recoverETH()` / `recoverTokens()`
- No `receive()` with a sweep
- No admin withdrawal of any kind

`RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` add only `getLatestRate()` overrides and introduce no recovery path: [3](#0-2) [4](#0-3) 

By contrast, `LineaMessenger` — another fee-paying bridge helper in the same codebase — inherits `Recoverable` and additionally enforces `msg.value == value` to prevent any ETH from being trapped: [5](#0-4) [6](#0-5) 

`Recoverable.recoverETH()` provides the pattern that is absent here: [7](#0-6) 

## Impact Explanation
Any ETH sent to `updateRate()` beyond the exact sum of on-chain `estimatedFee` values is permanently frozen in the contract with no recovery path for any role. This matches **Critical — Permanent freezing of funds** in the allowed impact scope. The contract is non-upgradeable (no proxy pattern), so there is no administrative path to rescue the locked ETH once it accumulates.

## Likelihood Explanation
`updateRate()` is an unrestricted public `payable` function. Callers must estimate the total fee off-chain before calling; because on-chain fee estimates can shift between the off-chain query and block inclusion, callers routinely send a small buffer above the estimate to avoid reverts. Every such call that overshoots leaves a residual. Both `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` are rate-propagation contracts expected to be called repeatedly over their operational lifetime, so residuals accumulate continuously with no recovery path.

## Recommendation
Add an owner-restricted ETH recovery function to `MultiChainRateProvider`, or have it inherit `Recoverable` (as `LineaMessenger` does):

```solidity
function recoverETH(address recipient, uint256 amount) external onlyOwner {
    require(recipient != address(0));
    require(amount > 0 && address(this).balance >= amount);
    (bool success,) = payable(recipient).call{ value: amount }("");
    require(success, "Transfer failed");
}
```

Alternatively, enforce exact payment by reverting if `msg.value` exceeds the total estimated fee computed inside the loop, analogous to `LineaMessenger`'s `MismatchedMsgValue` guard.

## Proof of Concept
1. Deploy `RSETHMultiChainRateProvider` with two `rateReceivers` on different chains.
2. Call `estimateTotalFee()` → returns `0.02 ETH` (0.01 ETH per receiver).
3. Call `updateRate{ value: 0.025 ETH }()` from any EOA.
4. The loop sends `0.01 ETH` to LayerZero for receiver 0, then `0.01 ETH` for receiver 1.
5. `address(contract).balance` is now `0.005 ETH`.
6. Enumerate every function in `MultiChainRateProvider`, `RSETHMultiChainRateProvider`, and `AGETHMultiChainRateProvider` — none can move this balance.
7. Repeat step 3 on every subsequent rate update; balance grows monotonically and is irrecoverable.

Foundry fork test: assert `address(provider).balance == msg.value - totalFeeUsed` after each `updateRate` call, then assert every external call to the contract reverts or leaves the balance unchanged. [8](#0-7)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L13-13)
```text
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L9-9)
```text
contract RSETHMultiChainRateProvider is MultiChainRateProvider {
```

**File:** contracts/agETH/AGETHMultiChainRateProvider.sol (L12-12)
```text
contract AGETHMultiChainRateProvider is MultiChainRateProvider {
```

**File:** contracts/bridges/LineaMessenger.sol (L15-15)
```text
contract LineaMessenger is IL2Messenger, Recoverable {
```

**File:** contracts/bridges/LineaMessenger.sol (L36-37)
```text
        if (msg.value != value) revert MismatchedMsgValue(); // Ensure the sent value matches the expected value to
        // avoid trapping ETH in this contract
```

**File:** contracts/utils/Recoverable.sol (L64-73)
```text
    function recoverETH(address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (address(this).balance < amount) revert InsufficientBalance();

        (bool success,) = payable(recipient).call{ value: amount }("");
        if (!success) revert TransferFailed();

        emit ETHRecovered(recipient, amount);
    }
```

Audit Report

## Title
Excess ETH Permanently Frozen in `updateRate()` — (File: contracts/cross-chain/MultiChainRateProvider.sol)

## Summary
`MultiChainRateProvider.updateRate()` is a public `payable` function with no access control that forwards exactly `estimatedFee` per destination chain to LayerZero. Any ETH sent by the caller beyond `sum(estimatedFees)` remains in the contract permanently. Neither the abstract base contract nor either concrete implementation (`RSETHMultiChainRateProvider`, `AGETHMultiChainRateProvider`) inherits `Recoverable` or provides any ETH sweep/rescue function.

## Finding Description
In `MultiChainRateProvider.updateRate()` (L108–137), the loop calls `ILayerZeroEndpoint.send{ value: estimatedFee }(...)` for each configured receiver, forwarding only the freshly-estimated fee per chain. The `payable(msg.sender)` refund address passed to LayerZero handles only intra-call excess within each individual LayerZero `send` — it does not return the difference between `msg.value` and `sum(estimatedFees)` to the caller. After the loop completes, any remaining ETH balance in the contract has no path out.

The abstract contract inherits only `Ownable` and `ReentrancyGuard` (L13). Both concrete implementations — `RSETHMultiChainRateProvider` (L9) and `AGETHMultiChainRateProvider` (L12) — override only `getLatestRate()` and add no recovery mechanism. The codebase does contain a `Recoverable` utility (L14 of `contracts/utils/Recoverable.sol`) with `recoverETH()`, but neither the base nor either concrete implementation inherits it.

Contrast with `CrossChainRateProvider.updateRate()` (L96), which passes `send{ value: msg.value }` — forwarding the entire caller-supplied ETH to LayerZero, which then handles all refunds. `MultiChainRateProvider` deliberately splits the payment across multiple chains but omits the corresponding post-loop refund.

## Impact Explanation
Any ETH in excess of `sum(estimatedFees)` is permanently frozen in the contract. Because no recovery function exists anywhere in the inheritance chain, neither the owner nor any other party can retrieve it. This satisfies **Critical — Permanent freezing of funds**.

## Likelihood Explanation
`updateRate()` has no access control — any external account can call it. Callers are expected to use `estimateTotalFee()` to size their payment, but fee estimates from LayerZero are volatile and callers routinely add a safety buffer to avoid reverts. Any buffer, however small, is silently trapped. The condition is reachable on every call where `msg.value > sum(estimatedFees)`, which is the normal operating pattern.

## Recommendation
After the loop, refund any remaining ETH to the caller:

```solidity
uint256 remaining = address(this).balance;
if (remaining > 0) {
    (bool success,) = payable(msg.sender).call{value: remaining}("");
    require(success, "Refund failed");
}
```

Alternatively, inherit `Recoverable` (already present at `contracts/utils/Recoverable.sol`) to allow the owner to recover stranded ETH, and document that callers should send exact amounts.

## Proof of Concept
1. Deploy `RSETHMultiChainRateProvider` with two rate receivers on different chains.
2. Call `estimateTotalFee()` — suppose it returns `0.01 ETH`.
3. Call `updateRate{ value: 0.02 ether }()` — a 2× buffer, standard practice.
4. The loop executes twice, each time calling `send{ value: estimatedFee }` (≈ `0.005 ETH` each), consuming ≈ `0.01 ETH` total.
5. LayerZero refunds any intra-call excess directly to `msg.sender` via the refund address — but the `0.01 ETH` difference between `msg.value` and `sum(estimatedFees)` never leaves `MultiChainRateProvider`.
6. `address(multiChainRateProvider).balance == 0.01 ether`. No function exists to recover it. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L96-98)
```text
        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L9-28)
```text
contract RSETHMultiChainRateProvider is MultiChainRateProvider {
    address public immutable rsETHPriceOracle;

    constructor(address _rsETHPriceOracle, address _layerZeroEndpoint) {
        rsETHPriceOracle = _rsETHPriceOracle;

        rateInfo = RateInfo({
            tokenSymbol: "rsETH",
            tokenAddress: 0xA1290d69c65A6Fe4DF752f95823fae25cB99e5A7, // rsETH token address on ETH mainnet
            baseTokenSymbol: "ETH",
            baseTokenAddress: address(0) // Address 0 for native tokens
        });

        layerZeroEndpoint = _layerZeroEndpoint;
    }

    /// @notice Returns the latest rate from the rsETH contract
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/agETH/AGETHMultiChainRateProvider.sol (L12-31)
```text
contract AGETHMultiChainRateProvider is MultiChainRateProvider {
    address public immutable agETHPriceOracle;

    constructor(address _agETHPriceOracle, address _layerZeroEndpoint) {
        agETHPriceOracle = _agETHPriceOracle;

        rateInfo = RateInfo({
            tokenSymbol: "agETH",
            tokenAddress: 0xe1B4d34E8754600962Cd944B535180Bd758E6c2e, // agETH token address on ETH mainnet
            baseTokenSymbol: "ETH",
            baseTokenAddress: address(0) // Address 0 for native tokens
        });

        layerZeroEndpoint = _layerZeroEndpoint;
    }

    /// @notice Returns the latest rate from the agETH rate provider contract
    function getLatestRate() public view override returns (uint256) {
        return IAgEthRateProvider(agETHPriceOracle).getRate();
    }
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

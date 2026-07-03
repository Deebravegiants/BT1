### Title
Single-step `updateLayerZeroEndpoint` in `CrossChainRateReceiver` permanently freezes cross-chain rsETH rate, enabling stale-rate over-minting that dilutes existing holders - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

### Summary
`CrossChainRateReceiver` exposes `updateLayerZeroEndpoint()` and `updateRateProvider()` as single-step, immediately-effective setters. If either is set to a wrong address in one transaction, the `lzReceive()` gate is permanently broken with no recovery path. All L2 pools that read `rsETHOracle.getRate()` from this receiver then operate on a stale rate. When the real rsETH/ETH price on L1 rises above the frozen rate, any depositor can mint more rsETH per ETH than the current backing warrants, extracting value from existing rsETH holders.

### Finding Description
`CrossChainRateReceiver.lzReceive()` enforces two address checks before accepting a rate update:

```solidity
require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");
...
require(srcAddress == rateProvider, "Src address must be provider");
```

Both `layerZeroEndpoint` and `rateProvider` are set through single-step owner-only functions:

```solidity
function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
    layerZeroEndpoint = _layerZeroEndpoint;          // takes effect immediately
    emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
}

function updateRateProvider(address _rateProvider) external onlyOwner {
    rateProvider = _rateProvider;                    // takes effect immediately
    emit RateProviderUpdated(_rateProvider);
}
```

If the owner accidentally supplies a wrong address (e.g., a typo, a stale address from a previous deployment), the new value takes effect in the same transaction. There is no pending-state, no confirmation from the new address, and no time window to cancel. The legitimate LayerZero endpoint or rate provider is immediately locked out of `lzReceive()`, and the stored `rate` is frozen at its last value forever.

The frozen rate is then consumed by every L2 pool that points its `rsETHOracle` at this receiver. For example, `RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, and `RSETHPoolNoWrapper` all call:

```solidity
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();   // reads the frozen rate
}
```

and use it to compute the rsETH amount given to depositors:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

### Impact Explanation
As rsETH accrues staking rewards on L1, its true ETH backing per token rises. If the cross-chain rate is frozen below the true value, the denominator `rsETHToETHrate` is smaller than it should be, so every depositor receives more rsETH per ETH than the current backing justifies. The excess rsETH is unbacked, diluting the redemption value of every existing rsETH holder. This constitutes theft of unclaimed yield from existing holders, classified as **High**.

### Likelihood Explanation
The owner must make a configuration mistake — a typo, copy-paste error, or use of a stale address — when calling `updateLayerZeroEndpoint` or `updateRateProvider`. This is a realistic operational risk, especially during infrastructure migrations or redeployments. The original report's scenario (Alice accidentally enters the wrong address) maps directly here. Once the mistake is made, there is no on-chain mechanism to detect or revert it before the damage propagates to depositors.

### Recommendation
Apply a two-step commit-confirm pattern for both setters, analogous to OpenZeppelin's `Ownable2Step`:

1. **Propose**: store the candidate address in a `pendingLayerZeroEndpoint` / `pendingRateProvider` variable and emit an event.
2. **Accept**: require a separate transaction (ideally from the new address itself, or after a time delay) to activate the change.

This gives operators a window to detect and cancel an erroneous proposal before it affects `lzReceive()`.

### Proof of Concept

1. Owner calls `updateLayerZeroEndpoint(0xDEAD...BEEF)` with a wrong address. The change takes effect immediately. [1](#0-0) 

2. The real LayerZero endpoint calls `lzReceive(...)`. The check `require(msg.sender == layerZeroEndpoint)` fails because `layerZeroEndpoint` is now `0xDEAD...BEEF`. The rate is permanently frozen. [2](#0-1) 

3. rsETH accrues staking rewards on L1; the true rate rises from, say, 1.05e18 to 1.10e18, but the receiver still reports 1.05e18.

4. A depositor calls `RSETHPool.deposit{value: 1 ether}("")`. The pool reads the stale rate: [3](#0-2) 

   With the stale rate of 1.05e18 the depositor receives `1e18 * 1e18 / 1.05e18 ≈ 0.952 rsETH`. At the correct rate of 1.10e18 they should receive only `≈ 0.909 rsETH`. The extra `≈ 0.043 rsETH` is unbacked, diluting all existing holders.

5. The same stale rate is consumed by `RSETHPoolV2`, `RSETHPoolV3`, and `RSETHPoolNoWrapper` through their respective `setRSETHOracle`-configured oracle, amplifying the impact across all L2 deployments. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L54-57)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-91)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");
```

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV2.sol (L311-314)
```text
    function setRSETHOracle(address _rsETHOracle) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        rsETHOracle = _rsETHOracle;
        emit OracleSet(_rsETHOracle);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L539-547)
```text
    /// @dev Sets the rsETHOracle address
    /// @param _rsETHOracle The rsETHOracle address
    function setRSETHOracle(address _rsETHOracle) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        rsETHOracle = _rsETHOracle;

        emit OracleSet(_rsETHOracle);
    }
```

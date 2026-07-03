### Title
`updateRate()` Sends LZ Message to `address(0)` When `rateReceiver` Is Uninitialized — (`contracts/cross-chain/CrossChainRateProvider.sol`)

---

### Summary

`CrossChainRateProvider.updateRate()` is callable by any address with no access control. Because `rateReceiver` is never set in `RSETHRateProvider`'s constructor, it defaults to `address(0)`. Any caller can invoke `updateRate()` before the owner calls `updateRateReceiver()`, causing a LayerZero message to be dispatched with `address(0)` as the remote destination — a message that is permanently undeliverable.

---

### Finding Description

`updateRate()` carries no `onlyOwner` or similar guard: [1](#0-0) 

`rateReceiver` is a plain storage variable with no initialisation in `RSETHRateProvider`'s constructor, so it holds `address(0)` until the owner explicitly calls `updateRateReceiver()`: [2](#0-1) [3](#0-2) 

Inside `updateRate()`, the remote address is built directly from `rateReceiver` with no zero-address check: [4](#0-3) 

That 40-byte blob (`address(0) ++ address(this)`) is then passed straight to `ILayerZeroEndpoint.send()`: [5](#0-4) 

LayerZero accepts the call on the source chain; the relayer then attempts delivery to `address(0)` on the destination chain, which has no `lzReceive` implementation, so the message is permanently stuck/dropped. Meanwhile, `rate` and `lastUpdated` are written on the provider side, giving a false impression that the update succeeded: [6](#0-5) 

---

### Impact Explanation

The `RSETHRateReceiver` on the destination chain never receives the rate update. Any protocol or AMM that reads the receiver's stale (or zero) rate will misprice rsETH for cross-chain users. No funds are directly lost from the contracts, matching the **Low — Contract fails to deliver promised returns, but doesn't lose value** scope.

---

### Likelihood Explanation

The window exists from deployment until the owner calls `updateRateReceiver()`. Any EOA or bot that monitors the mempool for new deployments can front-run the owner's setup transaction. Even without front-running, an accidental or automated call to `updateRate()` during the setup window triggers the same outcome.

---

### Recommendation

Add a zero-address guard at the top of `updateRate()`:

```solidity
function updateRate() external payable nonReentrant {
    require(rateReceiver != address(0), "CrossChainRateProvider: receiver not set");
    ...
}
```

Alternatively, require `rateReceiver` to be supplied in the constructor of `RSETHRateProvider` and validated there.

---

### Proof of Concept

```solidity
// 1. Deploy RSETHRateProvider (rateReceiver == address(0) by default)
RSETHRateProvider provider = new RSETHRateProvider(
    oracle, dstChainId, lzEndpoint
);
// owner has NOT called provider.updateRateReceiver() yet

// 2. Any unprivileged caller invokes updateRate with enough ETH for LZ fees
provider.updateRate{value: 0.01 ether}();
// LZ send() is called with remoteAndLocalAddresses = abi.encodePacked(address(0), address(provider))
// Message is dispatched to address(0) on destination chain — permanently undeliverable

// 3. Assert receiver state is unchanged
assertEq(RSETHRateReceiver(receiver).rate(), 0);
assertEq(RSETHRateReceiver(receiver).lastUpdated(), 0);
// Provider local state was written, but cross-chain delivery silently failed
```

### Citations

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L26-27)
```text
    address public rateReceiver;

```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-85)
```text
    function updateRate() external payable nonReentrant {
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L88-88)
```text
        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L90-92)
```text
        rate = latestRate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L96-98)
```text
        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L13-24)
```text
    constructor(address _rsETHPriceOracle, uint16 _dstChainId, address _layerZeroEndpoint) {
        rsETHPriceOracle = _rsETHPriceOracle;

        rateInfo = RateInfo({
            tokenSymbol: "rsETH",
            tokenAddress: 0xA1290d69c65A6Fe4DF752f95823fae25cB99e5A7, // rsETH token address on ETH mainnet
            baseTokenSymbol: "ETH",
            baseTokenAddress: address(0) // Address 0 for native tokens
        });
        dstChainId = _dstChainId;
        layerZeroEndpoint = _layerZeroEndpoint;
    }
```

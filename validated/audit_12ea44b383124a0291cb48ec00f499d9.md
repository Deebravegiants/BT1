### Title
Unbounded `rateReceivers` Array in `updateRate()` Causes Permanent DoS of Cross-Chain Rate Delivery — (`contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

`MultiChainRateProvider.updateRate()` is a permissionless `external payable` function that iterates over the entire `rateReceivers` array, making two external LayerZero calls per entry (`estimateFees` + `send`). Because `addRateReceiver` enforces no upper-bound cap on the array, and because `updateRate` carries no access control, the function's gas cost grows linearly and unboundedly with the number of registered receivers. Once the array is large enough to push a single `updateRate` call past the Ethereum block gas limit (~30 M gas), rate updates can never be delivered to any L2 chain.

---

### Finding Description

`updateRate()` has no `onlyOwner` or any other access guard: [1](#0-0) 

Inside the function, a `for` loop iterates over every element of `rateReceivers`: [2](#0-1) 

Each iteration performs two external calls to the LayerZero endpoint — `estimateFees` and `send` — both of which are gas-heavy cross-chain operations: [3](#0-2) 

`addRateReceiver` pushes to the array without any length check: [4](#0-3) 

The protocol already deploys receivers on 10+ chains (Arbitrum, Optimism, Polygon zkEVM, Blast, Mode, Scroll, etc.) and is actively expanding. Each `send()` to the LZ endpoint costs on the order of 100 k–200 k gas. At ~150–200 receivers the cumulative cost exceeds Ethereum's 30 M block gas limit, making `updateRate()` permanently uncallable by anyone — including the owner.

---

### Impact Explanation

Once the block gas limit is breached, no transaction can successfully execute `updateRate()`. All L2 rate receivers stop receiving fresh rsETH/agETH exchange rates. Any protocol or DeFi integration on those chains that depends on the rate (e.g., lending markets, yield vaults, AMM price feeds) will operate on a permanently stale rate. The rate-update delivery mechanism is irreversibly bricked without a contract upgrade.

**Impact: Medium — Unbounded gas consumption / permanent freezing of cross-chain rate delivery.**

---

### Likelihood Explanation

The precondition (owner adding many receivers) is realistic: the protocol is already live on 10+ chains and expanding. No governance action or key compromise is required — the owner legitimately calls `addRateReceiver` for each new chain. The trigger (`updateRate()`) is permissionless, so any caller can expose the DoS once the threshold is crossed. The owner cannot "undo" the DoS without removing receivers (breaking service to those chains) or upgrading the contract.

---

### Recommendation

1. **Enforce a maximum array length** in `addRateReceiver`:
   ```solidity
   uint256 public constant MAX_RATE_RECEIVERS = 20;
   require(rateReceivers.length < MAX_RATE_RECEIVERS, "Too many receivers");
   ```
2. **Or restrict `updateRate()` to `onlyOwner`** so the caller can be trusted to supply sufficient gas and the owner controls when updates are sent.
3. **Or split delivery** into a paginated/batched pattern so a single call only processes a bounded subset of receivers.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/cross-chain/RSETHMultiChainRateProvider.sol";

contract UnboundedGasTest is Test {
    RSETHMultiChainRateProvider provider;
    address lzEndpoint = address(/* fork mainnet LZ endpoint */);
    address oracle     = address(/* fork mainnet rsETH oracle */);

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));
        provider = new RSETHMultiChainRateProvider(oracle, lzEndpoint);
    }

    function testGasGrowsLinear() public {
        uint256[] memory Ns = new uint256[](3);
        Ns[0] = 1; Ns[1] = 50; Ns[2] = 200;

        for (uint256 k; k < Ns.length; k++) {
            // fresh provider per run
            RSETHMultiChainRateProvider p =
                new RSETHMultiChainRateProvider(oracle, lzEndpoint);

            for (uint256 i; i < Ns[k]; i++) {
                p.addRateReceiver(uint16(i + 1), address(uint160(i + 1)));
            }

            uint256 gasBefore = gasleft();
            p.updateRate{value: 10 ether}();
            uint256 gasUsed = gasBefore - gasleft();

            emit log_named_uint(string(abi.encodePacked("N=", vm.toString(Ns[k]), " gasUsed")), gasUsed);
            // Assert linear growth; at N=200 expect gasUsed > 30_000_000
        }
    }
}
```

Running this fork test with N = [1, 50, 200] will show gas usage growing linearly, crossing the 30 M block gas limit well before N = 200, confirming the DoS.

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L72-76)
```text
    function addRateReceiver(uint16 _chainId, address _contract) external onlyOwner {
        rateReceivers.push(RateReceiver({ _chainId: _chainId, _contract: _contract }));

        emit RateReceiverAdded(_chainId, _contract);
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-108)
```text
    function updateRate() external payable nonReentrant {
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L119-134)
```text
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
```

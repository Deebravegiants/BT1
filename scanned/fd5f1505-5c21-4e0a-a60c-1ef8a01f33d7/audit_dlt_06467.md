# [M] `indexed` Keyword in Events Causes Data Loss for Dynamic Array Variables

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-07
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/27
Type: hats-finding

## Details
**Github username:** @MatinR1
**Twitter username:** MatinRezaii1
**Submission hash (on-chain):** 0xa5d3c41c908b75f7ae9a660281a4330a0e74ed0e31bef7ffebb42e3671eb5961
**Severity:** medium

**Description:**
**Description**\
when the `indexed` keyword is used for reference type variables such as dynamic arrays or strings, it will return the hash of the mentioned variables. 
Thus, the event which is supposed to inform all of the applications subscribed to its emitting transaction (e.g. front-end of the DApp, or the backend listeners to that event), would get a meaningless and obscure 32 bytes that correspond to keccak256 of an encoded string. This may cause some problems on the DApp side and even lead to data loss. For more information about the indexed events, check here:

(https://docs.soliditylang.org/en/v0.8.17/abi-spec.html?highlight=indexed#events)

The problem exists inside the `Penrose` contract. The event `ProtocolWithdrawal` is defined in such a way that the dynamical array of IMarkets is indexed. With doing so, the expected parameters wouldn't be emitted properly and front-end would get meaningless one-way hashes.

**Attachments**

1. **Proof of Concept (PoC) File**

Consider this scenario as an example:

1 - The function `withdrawAllMarketFees()` is called by the owner

2 - Inside the function `withdrawAllMarketFees()` we expect to see the the array of "IMarkets":

```
    function withdrawAllMarketFees(IMarket[] calldata markets_, ITwTap twTap) external onlyOwner notPaused {
        if (address(twTap) == address(0)) revert ZeroAddress();

        uint256 length = markets_.length;
        unchecked {
            for (uint256 i; i < length;) {
                _depositFeesToTwTap(markets_[i], twTap);
                ++i;
            }
        }

        emit ProtocolWithdrawal(markets_, block.timestamp);
    }
```
3 - But as the event topic is defined as indexed we'll get an obscure 32-byte hash and listeners will not be notified properly. Thus, the symbol of the token would be lost in the DApp.

For test purpose one can run this test file:

```Solidity

        event ProtocolWithdrawal1(IMarket[] markets, uint256 indexed timestamp);

    function test_emitter() public {

        IMarket[] memory markets = new IMarket[](3);
        markets[0] = (IMarket(address(45621)));
        markets[1] = (IMarket(address(16280123)));
        markets[2] = (IMarket(address(29378601)));

        emit ProtocolWithdrawal(markets, block.timestamp);
        emit ProtocolWithdrawal1(markets, block.timestamp);
    }
```

Outputs of test:

ProtocolWithdrawal:

```
		"from": "0xEF899724384f40905401fC81f35B015D85DD3d7c",
		"topic": "0xdc0aec64e01514853db7bc1f49a7321726ef185b59f680c9bc9edcf499722bc7",
		"event": "ProtocolWithdrawal",
		"args": {
			"0": {
				"_isIndexed": true,
				"hash": "0xbbc5483a19795bbbbd8c781bd967dd63baa732eedd40c64d80f20c8c3b688023"
			},
			"1": "1717769422"
		}
	}
```


ProtocolWithdrawal1:

```
		"from": "0xEF899724384f40905401fC81f35B015D85DD3d7c",
		"topic": "0x097571680426f67f82bf44d9b6367ca228e809c4d09dea150fa661f3d036148e",
		"event": "ProtocolWithdrawal1",
		"args": {
			"0": [
				"0x000000000000000000000000000000000000B235",
				"0x0000000000000000000000000000000000f86A3B",
				"0x0000000000000000000000000000000001C04829"
			],
			"1": "1717769422",
			"markets": [
				"0x000000000000000000000000000000000000B235",
				"0x0000000000000000000000000000000000f86A3B",
				"0x0000000000000000000000000000000001C04829"
			],
			"timestamp": "1717769422"
		}
```

As you can see, the intended outputs wouldn't be emitted if the `indexed` keyword is used for IMarkets[].

2. **Revised Code File (Optional)**

Consider modifying the event `ProtocolWithdrawal` inside the contract `Penrose`:

```diff
-    event ProtocolWithdrawal(IMarket[] indexed markets, uint256 indexed timestamp);
+    event ProtocolWithdrawal(IMarket[] markets, uint256 indexed timestamp);
```

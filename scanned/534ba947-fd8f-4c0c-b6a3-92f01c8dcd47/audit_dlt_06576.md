# [M] `VaultBitcoinWallet` contract can not disable `relayersWhitelist` via `toggleRelayersWhitelistEnabled()` function

## Summary
Severity: Medium
Chain: Smart contract
Component: illuminex
Published: 2024-07-03
Source: https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/issues/49
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x736df5661c79f6f5e6f46d0478e4371d1a07eaf8d93b49cf0869e8e75767e679
**Severity:** medium

**Description:**
**Description**\
`VaultBitcoinWallet.sol` contract has `startRefuelTxSerializing()` function. This function deploys `RefuelTxSerializer` contract since `VaultBitcoinWallet` contract as `msg.sender` will act as an `allowedCreator` and its implemented as:

```solidiy
    function startRefuelTxSerializing(bytes32 outgoingTxHash) public onlyRelayer {
        uint256 _index = _outboundTxHashToId[outgoingTxHash];

        OutboundTransaction storage outboundTx = outboundTransactions[_index];
        require(outboundTx.txHash != bytes32(0) && outboundTx.finalisedCandidateHash == bytes32(0), "UOT");

@>      RefuelTxSerializer _sr = refuelSerializerFactory.createRefuelSerializer(_serializers[_index]);
@>      _sr.toggleRelayer(msg.sender);

        _refuelSerializers[_index].push(_sr);
        emit RefuelTxStarted(_index, _refuelSerializers[_index].length - 1);
    }
```

`createRefuelSerializer()` is implemented in `refuelSerializerFactory.sol` as:

```solidity
    function createRefuelSerializer(TxSerializer parent) public returns (RefuelTxSerializer _serializer) {
@>        require(msg.sender == allowedCreator, "NAC");

        (uint64 outgoingTransferCost, uint64 incomingTransferCost) = parent.fees();
        (
            IScript vaultScript,
            IScript p2pkhScript,
            IScript p2wpkhScript,
            IScript p2shScript,
            IScript p2wshScript
        ) = parent.scriptSet();

        _serializer = new RefuelTxSerializer(
            parent,
            BitcoinUtils.WorkingScriptSet(vaultScript, p2pkhScript, p2wpkhScript, p2shScript, p2wshScript),
            AbstractTxSerializer.FeeConfig(outgoingTransferCost, incomingTransferCost)
        );

@>      _serializer.transferOwnership(msg.sender);

        isDeployedSerializer[address(_serializer)] = true;
        emit TransactionSerializerCreated(address(_serializer));
    }
```

TWO things to note here:-

1) As it can be seen, `RefuelTxSerializer` contract's ownership is transferred to `msg.sender` i.e `VaultBitcoinWallet.sol` contract.

2) `RefuelTxSerializer` contract inherits `AbstractTxSerializer` which further which sets `msg.sender` i.e `VaultBitcoinWallet.sol` contract as relayer.

```solidity
        _toggleRelayer(msg.sender);
```

```solidity
    function _toggleRelayer(address _relayer) internal {
        relayers[_relayer] = !relayers[_relayer];
    }
```

3) `RefuelTxSerializer.sol` as give in inheritance route, further inherits `AllowedRelayers.sol` contract which has below `onlyOwner` functions.

```solidity
    function toggleRelayersWhitelistEnabled() public onlyOwner {
        relayersWhitelistEnabled = !relayersWhitelistEnabled;
    }

    function toggleRelayer(address _relayer) public onlyOwner {
        _toggleRelayer(_relayer);
    }
```

Both of these functions can only be called the owner. Now as mentioned in point 1, `VaultBitcoinWallet.sol` is the owner of `RefuelTxSerializer` contract instance so it should be able to call the above `onlyOwner` function. so `VaultBitcoinWallet.sol` has called `toggleRelayer()` function to set the `msg.sender` of `VaultBitcoinWallet.createRefuelSerializer()` function which can be seen at [L-286](https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/blob/db34511e17fdf281aacef4267c300431d3ac12d7/packages/contracts/contracts/illuminex/xengine/chains/btc/wallet/VaultBitcoinWallet.sol#L286) in `VaultBitcoinWallet.sol`:

```solidity
        _sr.toggleRelayer(msg.sender);
```

Now, THE ISSUE is that, `VaultBitcoinWallet.sol` can not directly call inherited `toggleRelayersWhitelistEnabled()` function as `VaultBitcoinWallet` is a contract and NOT an EOA to call any function directly. There would need some pointer to call `toggleRelayersWhitelistEnabled()` function similar how `toggleRelayer()` function is called in `VaultBitcoinWallet` contract.

With this issue, it would not be possible to call `toggleRelayersWhitelistEnabled()` to enable or disable the `relayersWhitelist` which would decide the `onlyRelayer` use across contracts. This would break one of functionality where implemented `toggleRelayersWhitelistEnabled()` function can not be access by `VaultBitcoinWallet.sol`

**Recommendation to fix**\
To mitigate this issue, consider implementing function which can call `toggleRelayersWhitelistEnabled()` from `RefuelTxSerializer` .

For example understanding:

```diff
+    function relayer_toggleRelayersWhitelistEnabled(bytes32 outgoingTxHash, uint256 refuelTxId) public onlyOwner {
+        uint256 _index = _outboundTxHashToId[outgoingTxHash];

+        RefuelTxSerializer _sr = _refuelSerializers[_index][refuelTxId];
+        _sr.toggleRelayersWhitelistEnabled();

+    }
```

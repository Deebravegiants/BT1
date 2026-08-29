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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/issues/49_

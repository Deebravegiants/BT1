# [M] Referrer can steal commission from another referrer

## Summary
Severity: Medium
Contest weight: 0.6088
Dataset id: 3969
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Minting NFTs uses a referral system. Where the user minting can chose which referrer should get the commission from their mint. A mint costs 0.1 ETH and the referrer gets 25% of this, 0.025 ETH. A user gets tied to their first referrer and any subsequent mints will always send the mint commissions to this referrer, in ReferralMap::trySetReferrerForUser:
```solidity
// Only set referrer ID once per user
ShortString existingId = map._users[user];
if (!isValidId(map, existingId)) {
    map._users[user] = storedId;
    // Emit Event for off-chain tracking
    emit UserOnbardedWithId(storedId, user);
    return true;
}
return false;
```
Hence, if a referrer sees that a user is minting multiple NFTs for another referrer they can mint an NFT for this user first using their own referral code. As long as the original mint was for >= 5 NFTs they will profit from this. Since each mint costs 0.1 ETH and they gain 0.025 ETH in commission per NFTs. So for 4 mints they would break even and 5 mints gain 0.025 ETH.

## Proof of Concept
```solidity
it("lets other referrer can steal mint commission", async () => {
    const fixture = await loadFixture(deployHybridFixture);
    const { user, bridge, referrer, others, referral, genesis, nft } = fixture;
    const other = others[0];
    // malicious referrer front runs the original tx by minting one NFT for the user with their referral
    await bridge.connect(other).mintWithReferer(user, 1, {
        value: ethers.parseEther("0.1"),
    });
    // original tx using a referrer is executed
    await bridge.connect(user).mintWithReferer(referrer, 9, {
        value: ethers.parseEther("0.9"),
    });
    // user still has 10 NFTs (but only paid for 9)
    // original referrer got 0
    expect(await referral.totalCommissionEarned(referrer)).to.be.equal(0);
    // front running referrer got all the commission but only spent 0.1, thus made a 0.15 eth profit
    expect(await referral.totalCommissionEarned(other)).to.be.equal(ethers.parseEther("0.25"));
});
```

## Recommendation
Consider tracking the commission per purchase not only the first purchase. Blerb:

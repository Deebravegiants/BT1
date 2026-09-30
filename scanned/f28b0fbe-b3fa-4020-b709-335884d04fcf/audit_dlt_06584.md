# [M] General users can change their votes during the last hour

## Summary
Severity: Medium
Chain: Smart contract
Component: Fenix-
Published: 2024-07-10
Source: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/27
Type: hats-finding

## Details
**Github username:** @YanhuiJessica
**Twitter username:** --
**Submission hash (on-chain):** 0x68b89e66b9201bd2bf929fd388fce7d8ea043c6cfba3070de64576b2eb958cc3
**Severity:** medium

**Description:**
**Description**\
One hour before the end of a period is used to prepare for the closing of the current voting session. General users are prevented from voting to ensure that the tallying of votes can be conducted on a consistent set of data. The `vote()` function calls `_checkEndVoteWindow()`if the token is not whitelisted NFT. However, this check is missing for the `reset()` function, which would also affect the result.

**Attack Scenario**\

For tokens with a large weight, abstaining during the last hour of a period will greatly affect the results.

**Attachments**

1. **Proof of Concept (PoC) File**

https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/blob/353c8e8e24454336e805e5c0e11e4e9ae1491d03/contracts/core/VoterUpgradeableV1_2.sol#L356-L363

```js
function reset(uint256 _tokenId) external nonReentrant {
    _voteDelay(_tokenId);

    require(IVotingEscrow(_ve).isApprovedOrOwner(msg.sender, _tokenId), "!approved/Owner");
    _reset(_tokenId);
    IVotingEscrow(_ve).abstain(_tokenId);
    lastVoted[_tokenId] = _epochTimestamp() + 1;
}
```

2. **Revised Code File (Optional)**

Add the below lines before calling `_reset()`.

```js
IManagedNFTManager managedNFTManagerCache = IManagedNFTManager(managedNFTManager);
if (!managedNFTManagerCache.isWhitelistedNFT(_tokenId)) {
    _checkEndVoteWindow();
}
```

Paste the below test case after `vote cant be called by nft in last hour if not whitelisted` in `test/nest/VoterV1_2.test.ts`, and run `npx hardhat test --parallel --grep "reset should not be called by nft in last hour if not whitelisted"`

```js
it('reset should not be called by nft in last hour if not whitelisted', async () => {
    let userTokenId = await deployed.votingEscrow.create_lock_for.staticCall(
      ethers.parseEther('1'),
      182 * 86400,
      signers.otherUser1.address,
    );

    await deployed.votingEscrow.create_lock_for(ethers.parseEther('1'), 182 * 86400, signers.otherUser1.address);

    await time.increaseTo((await nextEpoch()) - 3600);

    await expect(voter.connect(signers.otherUser1).reset(userTokenId)).to.be.revertedWith('distribute window');
  });
```

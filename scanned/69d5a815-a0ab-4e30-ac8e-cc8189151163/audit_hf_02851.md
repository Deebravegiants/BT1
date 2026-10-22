# [M] Interface definition error

## Summary
Severity: Medium
Contest weight: 0.5986
Dataset id: 15920
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`MarketPlace.authRedeem()` call interface `ISwivel.authRedeem()` but Swivel contract does not have this method only method “authRedeemZcToken()“.

The result will cause `MarketPlace.authRedeem()` to fail forever, thus causing `ZcToken.withdraw()` to fail forever.

## Proof of Concept
```solidity
function authRedeem(uint8 p, address u, uint256 m, address f, address t, uint256 a) public authorized(markets[p][u][m].zcToken) returns (uint256 underlyingAmount) {
    .....
    ISwivel(swivel).authRedeem(p, u, market.cTokenAddr, t, a);
    .....
} else {
    .....
    ISwivel(swivel).authRedeem(p, u, market.cTokenAddr, t, amount);
    ....
}
```
```solidity
function authRedeemZcToken(uint8 p, address u, address c, address t, uint256 a) external authorized(marketPlace) returns(bool) {
    // redeem underlying from compounding
    if (!withdraw(p, u, c, a)) { revert Exception(7, 0, 0, address(0), address(0)); }
    // transfer underlying back to msg.sender
    Safe.transfer(IErc20(u), t, a);
    return (true);
}
```

## Recommendation
Swivel contract need declare “is ISwivel” and change method name.

Other contracts should also declare “is Iinterfacename” to avoid method name errors like IMarketPlace.

Duplicate of [#186](https://github.com/code-423n4/2022-07-swivel-findings/issues/186).

Main issue for the non-existent function call and interface definition error.

This shows a direct path to funds being locked, upgrading the severity (and all duplicates) to high. 

Hmm, I think this could go either way.
 
Technically because this is a redundant method meant to add compliance with EIP-5095, there aren’t actually user funds locked because they can follow the normal `redeem` workflow. So it is specifically that EIP-5095 compliance that would be broken.
 
Plus personally I’d also want to reward more interesting or critical errors rather than a mis-spelled or defined interface.
 
That said, I’d of course err towards the judge’s decision, but maybe that extra context helps ! 

@JTraversa - appreciate the note and context. 
 
Can we walk through that flow to confirm the code path? I would downgrade to M if there is an alternate flow.
 
We both agree this function doesn’t work - <https://github.com/code-423n4/2022-07-swivel/blob/fd36ce96b46943026cb2dfcb76dfa3f884f51c18/Marketplace/MarketPlace.sol#L148>
 
Which afaict also means that these calls are not functional either. 
 
<https://github.com/code-423n4/2022-07-swivel/blob/daf72892d8a8d6eaa43b9e7d1924ccb0e612ee3c/Creator/ZcToken.sol#L98>
 
<https://github.com/code-423n4/2022-07-swivel/blob/daf72892d8a8d6eaa43b9e7d1924ccb0e612ee3c/Creator/ZcToken.sol#L124>
 
Can you direct me to the alternate flow for redemption and I will confirm and move back to M

For sure!
 
So there are two ways to redeem. Given custody sits on Swivel.sol, one is to call the zcToken (ERC-5095), which then itself calls authorized methods that bubble up from zcToken -> marketplace -> swivel. This is the path that appears to be broken, the `authRedeem`.
 
That said, the primary path (the one we’ve used in previous Swivel versions) is one that starts with a redemption method directly on Swivel.sol, and has the instruction to burn bubbled down from swivel -> marketplace -> zcToken.
 
That is available on Swivel.sol here: [Link](https://github.com/code-423n4/2022-07-swivel/blob/fd36ce96b46943026cb2dfcb76dfa3f884f51c18/Swivel/Swivel.sol#L634)
 
And its call to Marketplace.sol here: [Link](https://github.com/code-423n4/2022-07-swivel/blob/fd36ce96b46943026cb2dfcb76dfa3f884f51c18/Marketplace/MarketPlace.sol#L176)
 
Hopefully that clarifies a bit :) 

Yup, thank you. Downgraded back to M as user funds are not locked given the alternate path.

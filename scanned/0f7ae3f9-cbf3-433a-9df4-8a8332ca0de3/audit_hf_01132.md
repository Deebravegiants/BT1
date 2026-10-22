# [M] Wrong `shareChange`

## Summary
Severity: Medium
Contest weight: 0.1911
Dataset id: 4692
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect conditional check inside the shareChange routine of the vToken contract, which computes the number of vTokens to mint when a user deposits underlying assets. The function currently tests whether the total supply of vTokens is greater than zero (if (_totalSupply > 0)) before applying the proportional minting formula. When the total supply equals the caller's existing share amount – a situation that can arise when all existing vTokens are held by a single address, such as the burn address – the condition passes, but the subsequent formula uses (_totalSupply - oldShares) as a multiplier. Because oldShares is equal to _totalSupply, the multiplier becomes zero, causing the computed newShares value to be zero even though the user supplied a positive amount of assets. As a result the user receives no new vTokens for their deposit, effectively losing the underlying funds they transferred. This edge case is rarely triggered because the protocol’s initialization sends all initial tokens to the dead address, and normal operation never burns tokens from that address. However, the contract includes an "orderer" role capable of burning tokens held by the burn address; if that role is exercised, the total supply can be reduced such that oldShares equals the total supply, activating the faulty path. The issue was discovered during a formal security audit by Code4rena, where the auditors examined the shareChange code and identified that the conditional does not account for the subtraction of the caller’s previous share amount. The bug is subtle because the contract behaves correctly for the vast majority of states, and the failing condition only appears when the total supply matches the user’s existing share, which is an uncommon state that may not surface during routine testing. From a user’s perspective the symptoms are stark: after depositing assets, the UI may show a successful transaction but the vToken balance remains unchanged or becomes zero, and the underlying assets appear locked or lost. The protocol’s accounting assumptions – that each deposited asset yields a proportional increase in vToken supply – are violated, breaking the invariant that total vToken supply reflects total underlying assets. Conceptually the flaw belongs to the class of arithmetic or logic errors where a boundary condition is not properly handled, leading to a division by zero‑like situation that yields a zero result instead of the expected positive share. The correct mitigation is to modify the guard to verify that the remaining supply after subtracting the caller’s old shares is positive (if (_totalSupply - oldShares > 0)) before applying the minting formula. This ensures that the multiplier never collapses to zero and that users receive the correct amount of vTokens for their deposits, preserving the financial integrity of the protocol.

## Proof of Concept
Base on the code in function `shareChange()` in [vToken.sol](https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/vToken.sol)  
Assume that if `oldShare = totalSupply > 0`,

* `newShares` = `(_amountInAsset * (_totalSupply - oldShares)) / (_assetBalance - availableAssets);`  
= `(_amountInAsset * (_totalSupply - _totalSupply)) / (_assetBalance - availableAssets);`  
= `0`  

It make no sense, because if `amountInAsset >> availableAssets`, `newShares` should be bigger than `oldShares`, but in this case `newShares = 0 < oldShares`

## Recommendation
Modify the [line](https://github.com/code-423n4/2022-04-phuture/blob/594459d0865fb6603ba388b53f3f01648f5bb6fb/contracts/vToken.sol#L160) from `if (_totalSupply > 0)` to `if (_totalSupply - oldShares > 0)`.

Such a case is considered impossible due to the fact that it can only work with a 0xdead address.

Agree it’s not an issue as on initialization tokens are sent to the burn address making this unlikely. ![image](https://user-images.githubusercontent.com/20556729/170049178-fdb37630-f807-44ac-9808-d42ed5a32102.png)

However the orderer role could possibly burn the tokens held by the burn address causing this issue to happen.

Agree with mitigation step:

Modify the [line](https://github.com/code-423n4/2022-04-phuture/blob/594459d0865fb6603ba388b53f3f01648f5bb6fb/contracts/vToken.sol#L160) from if (_totalSupply > 0) to if (_totalSupply - oldShares > 0)

If it were impossible for tokens to be burned from the 0xdead address then this wouldn’t be a concern.

So although extremely unlikely, this is valid.

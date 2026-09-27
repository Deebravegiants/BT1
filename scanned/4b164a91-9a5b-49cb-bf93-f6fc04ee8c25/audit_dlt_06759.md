# [M] Admin rug vectors

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-rubicon
Published: 2022-05-28
Source: https://github.com/code-423n4/2022-05-rubicon-findings/issues/249
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L216-L229
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L334-L337
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathToken.sol#L269-L272


# Vulnerability details

## Impact
There are multiple functions that the admin can call to brick various parts of the system, leading to user's funds being locked

Even if the owner is benevolent the fact that there is a rug vector available may [negatively impact the protocol's reputation](https://twitter.com/RugDocIO/status/1411732108029181960). See [this](https://github.com/code-423n4/2021-08-realitycards-findings/issues/73) example where a similar finding has been flagged as a high-severity issue. I've downgraded these instances to be a medium since it requires cooperation of the admin.

## Proof of Concept
Here are some examples:
Overwrite state:
```solidity
File: contracts/rubiconPools/BathHouse.sol   #1

216       /// @notice A migration function that allows the admin to write arbitrarily to tokenToBathToken
217       function adminWriteBathToken(ERC20 overwriteERC20, address newBathToken)
218           external
219           onlyAdmin
220       {
221           tokenToBathToken[address(overwriteERC20)] = newBathToken;
222           emit LogNewBathToken(
223               address(overwriteERC20),
224               newBathToken,
225               address(0),
226               block.timestamp,
227               msg.sender
228           );
229       }
```
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L216-L229

Steal new funds with new malicious market
```solidity
File: contracts/rubiconPools/BathHouse.sol   #2

334       /// @notice Admin-only function to set a Bath Token's target Rubicon Market
335       function setMarket(address newMarket) external onlyAdmin {
336           RubiconMarketAddress = newMarket;
337       }
```
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L334-L337

Add a ton of bonus tokens, making withdrawals break because of unbounded for-loop
```solidity
File: contracts/rubiconPools/BathToken.sol   #3

269       /// @notice Admin-only function to add a bonus token to bonusTokens for pool incentives
270       function setBonusToken(address newBonusERC20) external onlyBathHouse {
271           bonusTokens.push(newBonusERC20);
272       }
```
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathToken.sol#L269-L272

## Tools Used
Code inspection

## Recommended Mitigation Steps
Validate input arguments and require specific upgrade paths for each contract, not just allowing the admin to set whatever they decide, add limit to number of bonus tokens

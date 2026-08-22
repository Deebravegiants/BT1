# [H] Incorrect check of stale price can lead to DoS and the use of a stale price in the Ibo contract

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/14
Type: hats-finding

## Details
**Github username:** @neumoxx
**Submission hash (on-chain):** 0x51d705a546da3ec2c5b131aeafd5ef000902ca9c02fd7483d6580226b6312672
**Severity:** high

**Description:**
## Vulnerability Report
**Description**
There is a reentrancy bug in the `LiquidityPool` contract that allows a malicious actor to alter the number of shares to transfer to the `WithdrawRequestNFT` contract when calling `requestWithdraw`.

We can see that the call to `requestWithdraw` in the `LiquidityPool`:
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/LiquidityPool.sol#L199-L210

Calls `requestWithdraw` in the `WithdrawRequestNFT` contract:
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/WithdrawRequestNFT.sol#L57-L66

And in this last call, there is a call to `_safeMint`. This function, from the OpenZeppelin library, ends up calling `_checkOnERC721Received`, which makes a call to the recipient of the NFT in case it is a contract that implements the `IERC721Receiver` interface:

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/94697be8a3f0dfcd95dfb13ffbd39b5973f5c65d/contracts/token/ERC721/ERC721.sol#L465-L482


This opens up the attack, where the malicious actor takes control of the execution flow before the transfer of `eETH` takes place in line 205 of the `LiquidityPool` contract:
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/LiquidityPool.sol#L205

This way the attacker can create a WithdrawRequestNFT with a certain amount of shares, and when the `_safeMint` call gives them the execution flow, they can call `withdraw` on a previously minted NFT. This would burn the shares from that particular NFT, lowering the amount of `totalShares` of the `EETH` contract and thus provoking that, when the execution flow returns to the `LiquidityPool` contract, the amount of shares transferred from the user to the NFT contract would be less than the amount previously passed to the `WithdrawRequestNFT` in line 203:
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/LiquidityPool.sol#L203


**Attack Scenario**
Now these would be the steps Alice could perform to attack the contract.
1. Alice creates a contract that implements the `IERC721Receiver` interface and puts her attack code in the `onERC721Received` of such contract. 
2. She calls `requestWithdraw`  of the `LiquidityPool` contract
passing as recipient the malicious contract crafted in step 1. The amount passed to the function corresponds to a certain amount of shares returned by function `sharesForAmount`.
3. Contract `WithdrawRequestNFT` mints an NFT to the malicious contract with the amount requested and its corresponding shares. Here, the malicious contract takes control.
4. The contract calls `deposit` in the `LiquidityPool` contract (note that Alice must be whitelisted to make this call). This action transfers ETH from Alice to the contarct and mints the corresponding shares, increasing the total amount of shares in the system.
5. Then, the flow returns to the `WithdrawRequestNFT` and then the `LiquidityPool`, where there is a transfer of eETH from the user to the NFT contract. But this transfer also uses function `sharesForAmount` to calculate the shares that must be subtracted from Alice's balance. Now, total shares calculated, because of the deposit performed by Alice in the middle of the call, are less than before.
6. Now, a certain amount of eETH shares from Alice have been transferred to the `WithdrawRequestNFT` contract, but the number of shares recorded in the WithdrawRequestNFT is higher.
7. To make a profit, Alice will have to wait for the shares to increase in value in respect to the amount of the withdraw request, because function `getClaimableAmount` returns the minimum of the amount recorded in the NFT and the shares recorded converted to amount (minus fees), using function `amountForShare`. As the amount for shares are less than they should be, due to the deposit, it's better to wait some time until some rewards are accrued and the claimable amount is higher.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/14_

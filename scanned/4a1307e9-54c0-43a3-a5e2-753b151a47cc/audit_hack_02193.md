# [M] Seven ways in which the Owner and Proxy Admin can make users lose funds ("rug vectors")

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2022-02-badger-citadel/blob/main/contracts/TokenSaleUpgradeable.sol#L15
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2022-02-badger-citadel/blob/main/contracts/TokenSaleUpgradeable.sol#L15


# Vulnerability details

The contest explicitly asks to analyze the contract for "Rug Vectors", so that is what this issue is about. 

(**note to reviewers** This issue list maybe 7 different problems and recommends different fixes. I could have made seven separate issues for each, but it would be annoying for for you guys to read and for me to write, so I hope I'm doing the right thing here and you guys will count it as such :))

I have classified this issue as "high risk" - although the vulnerability is considerable, the attacks themselves are not very likely to occur (they depend on the owner and/or the proxy admin to be compromised). The main reason why I believe the vulnerabiity is "high" is because the very fact that all these factors exist can make the sale fail, as informed users will avoid the contract completely one they realize the extent in which the contract is manipulable. 


In the current implementation, there several ways that investors can lose funds if the owner of the contract is not well behaved. These risks can be divided into two kinds:

- owner becomes unable to act (for example, owner looses her private key, or the owner is a wallet or a DAO and signers cannot agree on the right action to take)
- owner is malicious  (for example, the owner account gets hacked or the signers turn bad), and wants to steal as much as the funds as possible ("Rug Vectors"), or executes a griefing attack (i.e. acts in such a way to hurt the buyers and/or the project, without immediate financial gain)

The contract is vulnerable to all three types of vulnerabilities ("rug pull", "griefing" and "inactivity"). 

(1) Loss of funds due to owner inactivity:
  (1a) If the owner does never funds the contract, the buyers will not receive their tokens, and have no recourse to get their investment back
  (1b) If the owner does not call `finalize`, buyers will not receive their tokens, and and have no recourse to get their investment back

(2) Griefing attacks by the owner (attacks that that have no immediate gain for the attacker, but are either annoying or lead to loss of funds)
  (2a) the owner can change many essential conditions of the sale: for example, the price, the start time, the duration, the guest list, and the total amount of tokens that are allowed to be sold. The owner can do this at any moment, also __while the sale is in course__. This allows for all kinds of griefing attacks. It also voids the whole point of using a smart contract in the first place.
  (2b) Owner can pause the contract at any time, which will freeze the funds in the contract, as it also disallows users to claim their tokens

(3) Rug pull by owner (attacks with financial gain for the attacker, buyer loses money)
  (3a) The Owner can call `sweep` at any time and remove all unsold CTDL tokens while the sale is in progress. Future buyers will still be able to buy tokens, but the sale can never be finalized (unless the owner funds the contract)
  (3b) Owner can front-run buyers and change the price. I.e. the owner can monitor the mem pool for a large `buy` transaction and precede the transaction with her own transaction that changes the price to a very low one. If the price is low enough, `getAmountOut` will return `0`, and the buyers will lose her funds and not receive any CTDL tokens at all.

(4) Rug pull by proxy Admin
  (4a) Although no deployment script is provided in the repo, we may assume (from the tests and the fact that the contracts are upgradeable) that the actual sale will be deployed as a proxy. The proxy admin (which may not be the same account as the owner) can change the implementation of the contract at any time, and in particular can change the implemention logic in such a way that all the funds held by the contract can be sent to the attacker.


Recommendations:
- In general, I would recommend to not write your own contract at all, but instead use OpenZeppelin's crowdsale contract: https://docs.openzeppelin.com/contracts/2.x/api/crowdsale#Crowdsale which seems to fit your needs pretty well
- To address 1a and 3a, enforce that the contract is funded  with enough CTDL tokens _before_ the sale starts (for example, as part of the initialize logic)
- To adress 1b, simply remove the "onlyOwner" modifier on the "finalize()" function so that it can be called by anyone 
- To (partially) address 2a, reduce the extent to which the owner can change the sale conditions during the sale (in any case remove the setSaleStart, setSaleEnd, setTokenInLimit or limit their application to before the sale starts). Ideally, once the sale starts, conditions of the sale remain unchanged, or change in a predictable way
- To address 2b, leave the tokens of the buyer in the contract (instead of sending them to a `saleRecipient` and implement an `emergencyWithdraw` function that will work also when the contract is paused, and that allows buyers can use to retrieve their original investment in case something goes wrong 
- To address 3a, allow the owner to call `sweep` only after the sale is finalized 
- To address 3b, either do not allow to change the token price during the token sale, or, if you must have this functionality, have the price change take effect only after a delay to make front-running by the owner impossible
- To address 4a, do not deploy the contract as a proxy at all (which seems overkill anyway, given the use case)

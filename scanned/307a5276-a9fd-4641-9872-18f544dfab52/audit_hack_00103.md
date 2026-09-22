# [C] Fei Rari exploit: Between approximately 9:00 and 9:35 AM UTC on April 30th, seven of Rari’s Fuse pools were drained for a total of ~$80M

## Summary
Severity: Critical
Target: Fei Rari
Loss: $80,000,000
Published: 05/01/2022
Source: https://rekt.news/fei-rari-rekt
Type: rekt-postmortem

## Details
## Fei Rari - REKT 2

 Sunday, May 1, 2022 Fei - Rari - REKT 

 read this article also in : zh 

 Fei Rari - rekt. 
 Between approximately 9:00 and 9:35 AM UTC on April 30th, seven of Rari’s Fuse pools were drained for a total of ~$80M.

 Despite claiming “ none of the arbitrum pools are vulnerable ”, the attack continued on Arbitrum today, though the losses (~100 ETH) were minimal in comparison.

 This isn’t the first time that Rari has got rekt - lets hope the hackers don’t go for a hat trick.

 Credit: Hacxyk , Certik 

 Rari uses forked Compound code, which doesn’t follow the check-effect-interaction pattern, and has led to a number of re-entrancy incidents: CREAM , Hundred , Voltage/Ola . 

 In this case though, the re-entrancy pattern is via CEther which uses call.value to send ETH. In the case of the receiver being a contract, call.value is able to make another call which can be abused.

 This vulnerability was reported in early March and mitigated by upgrading the CToken and Comptroller contracts. However, the new re-entrancy protections didn’t cover the function exitMarket within the Comptroller contract.

 exitMarket re-assigns a deposited asset as no longer being collateral, which can then be withdrawn, as long as there is no loan taken against the funds. Given that the checks are made after the transfer (due to Compound code not following check-effect-interaction pattern), the transaction doesn’t record the borrowed amount as debt before the collateral is withdrawn.

 By using flash loans to borrow ETH, the attacker was able to re-enter via call.value , calling exitMarket in order to withdraw the flash loaned collateral whilst also keeping the borrowed ETH.

 Step-by-step using example tx 0xab4860… 

 1. Attacker flashloaned 150,000,000 USDC and 50,000 WETH

 2. Deposited 150,000,000 USDC as collateral into the fUSDC-127 contract, which is a vulnerable fork version of the compound protocol.

 3. With deposited collateral, the attacker borrowed 1,977 ETH via the “borrow()” function.

 4. However, the “borrow()” function does not follow the check-effect-interaction pattern. Specifically, it transfers ETH to the attacker’s contract before updating the attacker’s actual borrow records.

 5. Therefore, with the attacker’s borrow record not updated, the attacker made a reentrant call to “exitmarket()” in the fallback function, which allows the attacker to withdraw all his collateral (150M USDC)

 6. The attacker repeated steps 1~5 on multiple other tokens.

 7. Finally, the attacker repaid the flashloan and transferred the rest to their address as profit, and routed some of the funds onward to Tornado Cash.

 Affected Fuse pools: 8, 18, 27, 127, 144, 146, 156 

 Attacker’s address (inc. all exploit txs): 0x616275… 

 Attack contracts: 0xE39f3C… , 0x32075b… 

 Arbitrum attack tx: 0x3212d0… 

 Total funds lost: 

 6,037.8139071514 eth

 20,251,603.11559831 fei

 14,278,990.684390573 dai

 1,948,952.1788665l lusd

 10,055,556.328173 usdc

 132,959.9008 usdt

 31,615.8714 rai

 13,101,364.94 frax

 2,765,891 ust

 Total estimated value: $79,749,026 

 Following the attack, the hacker began depositing the proceeds into Tornado Cash, however stopped after moving just 5400 ETH (~$15M).

 With the remaining $62.7M still in the wallet, is the hacker considering the offer of a bounty to return the funds?

 Tribe DAO seems to be hopeful, as they sent the following message via etherscan. 

 We noticed you may be considering the no-questions-asked $10m offer. If you wish to take us up on this, please deposit the remaining funds to the Tribe DAO Timelock: 0xd51dbA7a94e1adEa403553A8235C302cEbF41a3c

 All Compound forks should take this opportunity to check their code for similar vulnerabilities.

 As 0x_b1 pointed out:

 this exploit had been fixed in Compound code some time ago, but was changed to its previous form in this commit by developers

 Hopefully the user who asked Rari if the Arbitrum pools were safe was not too badly affected, as they were reassured of their safety by Rari, only to fall victim to the same exploit today.

 A quick check could have prevented the double damage. 

 Now Rari shares #10 on the leaderboard. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] THORChain exploit: The hacker left a clear message for THORChain, but apparently it was not clear enough, as THORChain initially believed they had lost just $800k to a w

## Summary
Severity: High
Target: THORChain
Loss: $8,000,000
Published: 07/22/2021
Source: https://rekt.news/thorchain-rekt2
Type: rekt-postmortem

## Details
## THORChain - REKT 2

 Monday, July 26, 2021 THORChain - REKT 

 read this article also in : zh 

 THORChain took a hammering. 
 Recently the protocol was hit for $5M. 

 A second strike saw them lose another $8M.

 The hacker left a clear message for THORChain, but apparently it was not clear enough, as THORChain initially believed they had lost just $800k to a whitehat hacker.

 The tx data told a different story: 

 Source 
 THORChain has always used a very conversational tone from their official Twitter account, and they continued to do so even after the attack. 

 When you’ve lost over 10 million of your users' funds in 10 days, it’s not a good idea to celebrate an increase in followers. 

 The new followers arrived to watch you bleed, they are not a sign of your success. 

 The passion of the THORchain community remains high, but it manifests itself differently now that they are suffering.

 The following message was found in a transaction from a RUNE holder to the attacker.

 “Savage.” 

 What happened to cause such anger? 

 Credit: Halborn Security 

 The observation of an attack began on the 22.07.2021 - 21:42 GMT 

 An attacker targeted the Thorchain Bifrost component through the ETH Router contract.

 During the transactions, the following addresses are seen in the transactions. 

 Router: 0xc145990e84155416144c532e31f89b840ca8c2ce 

 Vault: 0xf56cba49337a624e94042e325ad6bc864436e370 

 Attack contract: 0x700196e226283671a3de6704ebcdb37a76658805 

 Attack wallet (spawned from Tornado Cash): 0x8c1944fac705ef172f21f905b5523ae260f76d62 

 The simple attack steps can be seen below.

 The attacker created a fake router (Contract Address), then a deposit event emitted when the attacker sent ETH.

 The attacker passes returnVaultAssets() with a small amount of ETH, but the router is defined as an Asgard vault.

 On the Thorchain Router, it forwarded ETH to the fake Asgard.

 This creates a fake deposit event with a malicious memo.

 Thorchain Bifrost intercepts as a normal deposit and refunds to an attacker due to a bad memo definition.

 Contract Address 

 Transaction 1 

 Transaction 2 

 Transaction 3 

 Transaction 4 

 Transaction 5 

 Transaction 6 

 Last Transaction By An Attacker 

 Transactions to THORChain pass user-intent with the MEMO field on the chains which contain custom user input. 

 The THORChain inspects the transaction object, as well as the MEMO in order to process the transaction, so care must be taken to ensure the MEMO and the transaction is valid. If not, THORChain will automatically refund. (Reference.) 

 The hacker targeted a refund logic. The attack can be named as Lack of proper multi-event handling.

 Impact (~$8M USD)

 966.62 ALCX 

 20,866,664.53 XRUNE 

 1,672,794.010 USDC 

 56,104 SUSHI 

 6.91 YFI 

 990,137.46 USDT 

 The price of RUNE dropped by 25% , however, holders were about to receive more bad news. 

 Just as with the previous exploit, a vulnerability present due to decisions actively made by developers was found within the RUNE token contract code. 

 Hours after the attack, many addresses began to receive a previously unknown token; UniH.

 Those who tried to sell this token had their full RUNE balances drained upon approving its use.

 RUNE’s transferTo function used tx.origin instead of msg.sender, something explicitly advised against within the Solidity documentation as it allows interactions with malicious contracts to move your RUNE.

 In this case, granting approval to a protocol to spend UniH was all it took for any RUNE in a wallet to be stolen, as in this example. 

 As can be seen in the code’s comments this was a vulnerability that the team had foreseen, and had been acknowledged as “non-standard”.

 Another instance of the THORChain devs leaving instructions for the hackers. 

 Credit: Mudit Gupta 

 THORChain rekt again, and they have no one to blame but themselves. 

 Although perhaps not a DeFi “blue-chip”, THORChain were a well-established player, and many will be disappointed to see them go downhill so quickly.

 Why now, and in such quick succession? 

 Has something changed internally on the THORChain team, or did they upset somebody who had a motive to hurt them?

 An $8M payday would be enough motive for most, but this anonymous antihero left most of the loot behind…

 This was for power, not wealth. 

 What’s next for THORChain and their fanatical followers after such a string of major mistakes? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

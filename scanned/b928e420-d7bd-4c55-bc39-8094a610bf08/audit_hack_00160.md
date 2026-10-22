# [C] Meerkat Finance - BSC exploit: An impressive debut for the first major exploit on BSC, as Meerkat Finance head straight to number three on our leaderboard

## Summary
Severity: Critical
Target: Meerkat Finance - BSC
Loss: $32,000,000
Published: 03/04/2021
Source: https://rekt.news/meerkat-finance-bsc-rekt
Type: rekt-postmortem

## Details
## Meerkat Finance - BSC - REKT

 Thursday, March 4, 2021 BSC - Meerkat - REKT 

 read this article also in : zh 

 In retrospect, it was inevitable. 

 An impressive debut for the first major exploit on BSC, as Meerkat Finance head straight to number three on our leaderboard. 

 After just one day of operation, Meerkat Finance was rug pulled for 13 million BUSD and about 73,000 BNB, currently totalling around $31m.

 We’ve been watching Binance Smart Chain as they do their speed run through Ethereum’s DeFi summer. Now their copied codes have built up enough capital, and they have entered the rug pull phase.

 The aftermath presents an interesting situation. 

 Will CZ and team roll back their corporate chain, or allow their users to suffer the loss?

 This suricate scam leaves the thieves with nowhere to hide. 

 Where can they run to on such a small chain? Binance has closed the bridges , and even bscscan.com went down for a short while. Was this too much traffic, or some type of smokescreen?

 Meerkat Finance first claimed it was a hack but then deleted their accounts, leaving BSC users with only themselves, or maybe Binance to blame.

 With thanks to 0xdeadf4ce. 

- Meerkat Finance Deployer upgraded 2 vaults of the project. 

- 

- Attacker address called permissionless initialization function through the Vault proxies, effectively allowing anyone to become the Vault owner [2] 

- 

- Attacker subsequently drains Vaults by calling a function with signature 0x70fcb0a7 which accepts a token address as an input. Decompilation of the upgraded-to Smart Contract shows the only use of the invoked function to be removal of funds with the owner as beneficiary.

 Usually, if the contract has a function which allows the owner to retrieve the assets which are used in the strategy/vault actively, then you are placing your trust in the project team.

 They can pull the plug any time.

 That’s why projects like yearn add checks like in the image below, so that the team can only rescue the funds which are not in active use by the strategy/vault.

 Both affected Vaults used OpenZeppelin’s Transparent Proxy Upgrade pattern, allowing to upgrade the Vault logic to a new logic implementation by calling the function upgradeTo(address newImplementation) on the Vault proxy level.

 The BUSD Vault’s previous implementation is located at 0x49509a31898452529a69a64156ab66167e755dfb , the WBNB Vault’s previous implementation is located at 0x3586a7d9904e9f350bb7828dff05bf46a18bb271 , both being rather inconspicuous and verified contracts.

 Meerkat Finance Deployer calls upgradeTo() two times: 

- at block 5381239, setting WBNB Vault implementation to 0x9d3a4c3acee56dce2392fb75dd274a249aee7d57 

- at block 5381246, setting BUSD Vault implementation to 0xb2603fc47331e3500eaf053bd7a971b57e613d36 

 This changed the Vault logic to introduce two noteworthy functions that have not been part of the initial implementations.

- init(address owner)

- According to decompiled bytecode this function sets the address on storage slot 0 to the address provided to the function.

 There’s no permission check, making this newly added function the ultimate backdoor into the Vaults. 

 Using a specific Initializer pattern in transparent proxies is best-practice and was also applied in the first Vault implementations, so it is highly questionable what was the intend to add the init() method other than a planned theft of Vault funds.

- 0x70fcb0a7(address _param1)

 Source code is not available, decompiled source is limited to checking that the caller is equal to storage slot 0 set in init() method and transferring out the balanceOf() on the token contract supplied with param1, using the Vault address as the query target.
Both functions are not part of the previous Vault implementations.

 Comparing the bytecode size of old and new implementations it can be stated that the new implementation is only 1/4th the size of the previous logic.

 Since the upgrades were done by the Meerkat Finance Deployer the most likely scenario given all aspects of the on-chain data is an intentional “rug pull” while granted there is a small chance of private key compromisation.

 As of the time of writing funds have partially been split among various addresses and sent to what seemingly belongs to the Binance Bridge hosted by Binance exchange.

 The Binance.org Bridge is currently suspended, probably to avoid the funds from being easily moved to other chains.

 Timeline (04.03.2021) 

 Mar-04-2021 08:53:10 AM +UTC 
Meerkat Finance Deployer upgrades WBNB Vault to contract 0x9d3a4c3acee56dce2392fb75dd274a249aee7d57

 Mar-04-2021 08:53:31 AM +UTC 
Meerkat Finance Deployer upgrades BUSD Vault to contract 0xb2603fc47331e3500eaf053bd7a971b57e613d36

 Mar-04-2021 08:54:31 AM +UTC 
Attacker calls method 0x70fcb0a7 on BUSD Vault to transfer out 13,968,039 BUSD

 Mar-04-2021 08:54:55 AM +UTC 
Attacker calls method 0x70fcb0a7 on WBNB Vault to transfer out 73,635 WBNB

 The same games are played on different chains, but the balance of power is different. With CZ watching and the bridges burning, the robbers have nowhere to hide. 

 Even in the Meerkat_Rugpull Telegram group, chat members were not in total agreement of how they wanted Binance to handle the situation.

 Could Binance roll back the chain and refund their users? 

 The answer is not so clear - the 21 mystery validators could in theory arrange a refund, but it is unlikely. It would only fuel the CeDeFi issues and create more work for the (likely already stressed) BSC lawyers.

 Binance will have planned in advance how they would handle such a scenario. How they handle this case will set a precedent.

 Although this is not the first multimillion rugpull on BSC, it is the first since the rise of PancakeSwap and the increased user numbers that came along with it.

 Ignoring the unlikely event of someone from Binance stepping up to arrange a merkle distributor and returning the funds, the money is gone.

 So we find that protocols on BSC are no more secure than Ethereum. 

 CZ won’t save you. Their transactions are cheaper, but there’s no original development.

 What will become of this corporate chain once Eth L2 arrives? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

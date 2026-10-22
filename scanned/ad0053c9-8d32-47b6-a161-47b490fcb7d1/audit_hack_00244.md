# [H] Sovryn exploit: On the 4th of October, ~$1.1M was stolen from Sovryn, a “DeFi” protocol on the controversial “Bitcoin smart contract network”, RSK (apparently “the mo

## Summary
Severity: High
Target: Sovryn
Loss: $1,111,000
Published: 10/04/2022
Source: https://rekt.news/sovryn-rekt
Type: rekt-postmortem

## Details
## Sovryn - REKT

 Sunday, October 9, 2022 Sovryn - REKT 

 read this article also in : zh 

 More fuel for the maxis. 

 On the 4th of October, ~$1.1M was stolen from Sovryn, a “DeFi” protocol on the controversial “Bitcoin smart contract network”, RSK (apparently “the most secure smart contract network in the world”). 

 The devs placed contracts into “maintenance mode” preventing further losses and the attack was announced via a rather self-congratulatory written thread on Twitter.

 But, isn’t pausing contracts somewhat centralised, for a protocol catering to Bitcoiners?

 While truly Bitcoin-native DeFi apps remain impossible, good marketing attracts investors, and Sovryn was heavily-shilled by Anthony Pompliano upon launch last year, based on an erroneous claim that it had higher TVL than Uniswap v3, at almost $2B.

 The TVL turned out to be miscounted, including native staked SOV, leading to DeFiLlama’s addition of the staking toggle to their TVL metrics, and dropping Sovryn’s figure to just $52M.

 Since then, TVL is down approx 90% since peak and the native token SOV has dropped 99% from its ATH of one year ago.

 Credit: BeosinAlert 

 The protocol lost funds from two legacy lending pools: the RBTC (RSK-bridged BTC) pool, for 45 RBTC (~$900k), and the USDT pool, for 211k USDT. 

 According to Beosin’s analysis , the exploit was down to the “ external call of callTokensToSend function. ”

 Attacker’s address: 0xc92ebecda030234c10e149beead6bba61197531a 

 Example tx: 0xf5ea62… 

 The attacker first deploys the attack contract and transfers into 0.03 RBTC.

 Then invokes the attack contract to borrow 8.20 RBTC to three pair addresses via flashloan, then deposits the entire 8.23 RBTC.

 The attacker uses the LP to borrow 52,999 side tokens.

 The closeWithDeposit function is then called to repay the collateral. 26,900 side tokens were swapped for 4.17 RBTCs. Notice that the attacker minted 26,000 side tokens into 22,653 Load Token, while in the closeWithDeposit function, there is no such mint function.

 Then we found that the attacker used the side tokens to call the attack contract externally, and used the attack contract to call the mint function.

 Because in the tokenPrice function, it relies on the number of side tokens to calculate the Load token price, and the total number of tokens has not been updated at this time, resulting in the attacker getting more Load tokens.

 Finally, the attacker calls the burn function to burn 22,653 Load Token to get 27,086 side token.

 Then the attacker calls the related function in a loop to get the side token, and finally converts them to RBTC.

 The stolen funds were deposited into Tornado cash.

 An update posted on October 7th assures that no Sovryn individuals need to worry, stating that:

 Roughly half of the funds have been recovered so far

 Potential remaining user losses will be fully covered by the Exchequer

 And five days after the attack, a final announcement: 

 ”All user funds stuck on the ETH bridge have been unstuck. There is only once [sic] exception: the user bridging in USDT to XUSD.”

 There is no shortage of BTC-focused projects on Ethereum, including bridged assets such as WBTC/renBTC and protocols like Badger , but the scale of Bitcoin adoption remains low. 

 Even the largest of these, WBTC, with a TVL of ~$5B , barely scratches the surface of Bitcoin’s $387 billion market cap.

 BTC maxis don’t trust their coins to be wrapped onto other networks. Many are suspicious of Ethereum, DeFi and any experimentation regarding what they believe to be a pure cryptocurrency. 

 This incident will only give the bitcoiners even more reasons to cling onto their digital gold. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Voltage Finance exploit: Voltage Finance has been exploited for ~$4M via its “ Lending-as-a-Service ” partner Ola Finance on the Fuse Network

## Summary
Severity: High
Target: Voltage Finance
Loss: $4,000,000
Published: 03/31/2022
Source: https://rekt.news/voltage-finance-rekt
Type: rekt-postmortem

## Details
## Voltage Finance - REKT

 Thursday, March 31, 2022 Voltage Finance - Ola Finance - REKT 

 read this article also in : zh 

 Voltage Finance has been exploited for ~$4M via its “ Lending-as-a-Service ” partner Ola Finance on the Fuse Network. 

 Rather than a Compound fork, Ola describes itself as a “ a technology provider that enables others to build Compound-like instances ”.

 Earlier this month, a similar incident on the Gnosis / xDAI chain gave the teams using Compound’s code plenty of warning.

 But somehow, neither Voltage nor Ola got the news.

 If only there was somewhere developers could keep up to date with exploits in DeFi… 

 Similarly to the cases of Agave DAO and Hundred Finance , this exploit was due to a reentrancy vulnerability in the ERC 677 standard which Fuse Network uses for bridged tokens. 

 These token types include a callAfterTransfer() function which can be abused to make additional transfers before balances are updated (provided the underlying code does not follow the recommended checks-effects-interactions routine of execution).

 The original Compound code does not follow this pattern, however all proposed collateral tokens are vetted for this vulnerability before being added to the protocol.

 Credit: BlockSecTeam 

 Attacker’s address on Fuse: 0x371D7C9e4464576D45f11b27Cf88578983D63d75 

 Example tx (BUSD): 0x1b3e06b6b310886dfd90a5df8ddbaf515750eda7126cf5f69874e92761b1dc90 

 Attacker contract A: 0x632942c9BeF1a1127353E1b99e817651e2390CFF 

 Attacker contract B: 0x9E5b7da68e2aE8aB1835428E6E0c83a7153f6112 

 1: Contract A transfers 550 WETH to Contract B

 2: Contract B deposits 550 WETH, minting 27,284 oWETH

 3: Contract B borrows 507,216 BUSD

 4: Contract BUSD calls back to Contract B via callAfterTransfer() 

 5: Contract B transfers both 507,216 BUSD and 27,284 oWETH to Contract A.

 6: Contract A returns 27,284 oWETH to redeem initial deposit of 550 WETH and keeping the 507,216 BUSD as profit.

 As BlockSecTeam explain: 

 “ In the code logic of the borrow() function, the related internal states are updated after an external call. Specifically, the doTransferOut() function will invoke the transfer() function of the ERC677-based token, which will eventually lead to an external call. ”

 The above process was used repeatedly to take $USDC, $FUSD, $WBTC, $WETH & $FUSE.

 The resulting funds were first bridged to Ethereum (originally funded by Tornado Cash ) and then sent on to this address , where they remain in the form of ETH, WBTC, USDC (will Circle freeze these funds?) and FUSE, worth approximately $3.1M.

 When Agave and Hundred fell victim to the same attack vector, we said; 

 When one fork falls, all others have to check their foundations.

 Voltage Finance didn’t do that, and that’s why they’re taking their place (#64) on the leaderboard. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

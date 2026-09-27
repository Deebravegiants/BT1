# [C] Cream Finance exploit: Another failed experiment from the Yearn Finance ecosystem

## Summary
Severity: Critical
Target: Cream Finance
Loss: $130,000,000
Published: 10/27/2021
Source: https://rekt.news/cream-rekt-2
Type: rekt-postmortem

## Details
## Cream Finance - REKT 2

 Thursday, October 28, 2021 Cream - Yearn - REKT 

 read this article also in : zh 

 Another failed experiment from the Yearn Finance ecosystem. 

 Cream Finance has been hacked ( again ) for ~$130 million. 

 The Yearn Finance decentralised monopoly has grown too large, and its operators; too careless.

 Why accumulate so many protocols if you don’t care for their users? 

 We assumed that following the string of aggressive acquisitions by Yearn in 2020, we would see improved security on these platforms.

 However, that was clearly not the goal. 

 The CoinGecko Yearn Ecosystem page shows the price impact of this hack.

 That’s position number three on our leaderboard, the second entry for the Cream Finance protocol, and ten positions in total for the Yearn Ecosystem. 

 Whilst Yearn developers continue to make fast forks of other platforms, and incentivise users to use chains that work in their favour, they abuse the developers who worked on the original code, and put other users' funds at risk.

 This is not to say that Yearn seeks to trick their users - all DeFi degenerates are aware of the risks, but we can’t ignore this track record. 

 Business is business, whether on or off-chain. 

 Some of these protocols were picked up post-hack, but who had the most motive for those Yearn competitors to fail? 

 There was a clear advantage for Yearn in being able to link and leverage such a range of protocols, but with great power comes great responsibility…

 Who takes the blame for losing $130M? 

 credit: @Mudit__Gupta and @cryptofishx 

 Exploiter wallets: 

 Address A , Address B 

 The hacker was able to take advantage of a pricing vulnerability by repeatedly lending and borrowing flash-loaned funds across two addresses. 

 Next, after accumulating yUSDVault-collateralised crYUSD, the price of the underlying yUSDVault token was manipulated in order to effectively double the value of the collateral owned by the attacker.

 Finally, using the now overvalued collateral, the attacker drained CREAM’s lending vaults of as many assets as possible.

 A full table of the stolen funds, which include over 2760 ETH, a total of 76 BTC in renBTC, WBTC and HBTC, as well as tens of millions in stablecoins and other tokens, can be found here .

 Using address A, the attacker took a flash loan of 500M DAI from MakerDAO, depositing into Curve’s yPool for yDAI which was then used to mint yUSD. The yUSD was then deposited into Yearn’s yUSD strategy. 

 By using the yUSDVault tokens from Yearn as collateral on CREAM, the attacker then could mint ~$500M of crYUSD.

 With address B, the hacker then took a flash loan from AAVE worth $2B in ETH, to use as collateral on CREAM. This allowed for borrowing a further ~$500M of yUSD, which was deposited again in order to mint crYUSD.

 The two accounts then performed a loop of depositing and borrowing, with B transferring ~$500M in yUSDVault tokens to A each time, until account A was in possession of ~$1.5B in crYUSD and ~$500M yUSDVault.

 The attacker then exploited a vulnerability in CREAM’s internal PriceOracleProxy of yUSDVault tokens. The price of yUSDVault depends on its pricePerShare, which is defined by the vault’s yUSD balance / totalSupply yUSDVault.

 By redeeming ~$500M yUSDVault for the underlying yUSD, the attacker was able to decrease the vault’s totalSupply to just $8M. Combining this depletion with a deposit of ~$8M in yUSD into the vault led CREAM to increase the value of yUSDVault shares by approximately a factor of two.

 Due to the price manipulation, CREAM now sees address A as having $3B crYUSD in collateral. $2B of this was withdrawn in ETH in order to repay B’s flash loan while the ~$500m of yUSD redeeming from the yUSDVault pays off A’s DAI loan.

 The $1B left over was more than enough to drain (borrow and default) CREAM’s $130M assets available for lending. 

 Following the attack, funds were pulled from the exploit contract back to this wallet which had been funded by Tornado Cash around 30 mins before the attack in two transactions: one , two . 

 Since the attack, the hacker has been using the renBridge to send funds to BTC as well as adding over $40M CRETH2 in single-sided liquidity to Uniswap’s ETH-CRETH2 pool , presumably in an attempt to offload as much as possible as CRETH2 may be salvageable .

 The Cream.Finance: Deployer is amongst the many accounts who have tried to communicate with the hacker. 

 Their message ;

 you win. we're rekt. please return funds and we will honor a 10% bounty. 

 When experienced attackers make moves like this, the motives are not just financial.

 This is manipulation of the industry as well as the markets, and we must consider who stands to benefit.

 Other protocols were named in a mysterious message in the main exploit transaction’s input data; 

 gÃTµ Baave lucky, iron bank lucky, cream not. ydev : incest bad, dont do 

 In Mudit Gupta’ s Observations and Theories about the attack, he points out several reasons why he believes the hacker, (or hackers) to be experienced DeFi developers, and how it is not the average black hat attack.

 This hack revealed not only vulnerabilities in project code, but deeper rivalries that may not have been apparent for the average DeFi user. 

 A once hidden war is now being fought in public. 

 A $130M hack gets headlines, but for many, this attack will be remembered not for the loss, but for how it was used as a campaign tool by opposing teams, neither of which have come out on top.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

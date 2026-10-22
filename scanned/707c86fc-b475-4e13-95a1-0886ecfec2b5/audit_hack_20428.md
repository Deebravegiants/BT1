# [H] OtterSec: The $200m bluff: cheating oracles on Solana

## Summary
Severity: High
Published: Wed, 16 Feb 2022
Source: https://osec.io/blog/lp-token-oracle-manipulation/
Type: security-research

## Details
## The $200m bluff: cheating oracles on Solana

 OtterSec Feb 16, 2022 #solana How we fooled oracles to beat the house. An exploration into liquidity tokens and oracle price manipulation.

## Introduction 

 We discovered a vulnerability in Switchboardâs liquidity pool token price feeds, which could hypothetically allow an attacker to manipulate the price of liquidity pool tokens and possibly steal lending protocol funds. This was reported to all affected lending protocols.

 At the time of reporting, the following protocols were identified at risk:

 Protocol 
 Value 

 Apricot 
 $200m 

 Larix 
 $150m 

 Port 
 $100m 

 Tulip 
 $120m 

 Parrot.fi 
 $2m 

 We would also like to thank nojob for his contributions with the fair pricing of liquidity pool tokens.

## Background 

 Weâll first cover some relevant background concepts.

## AMMs 

 AMMs, or automated market makers, on Solana are onchain programs allowing users to swap between two tokens â for example, SOL and USDC. This process is automated, and the program helps âmake the marketâ by always allowing token swaps, hence the name automated market maker.

 AMMs have their own token accounts which they use in the token swap. The price, or amount of one token you can get for another, is solely defined by the token account amounts.

 This relationship can be modeled as a curve, where swapping tokens moves the price along the curve. For example, see this graph from the Stable Swap whitepaper :

 In this post, weâll be using constant product AMMs as our examples, but this vulnerability would apply to any AMM type.

## Liquidity pool tokens 

 In order to function, AMMs need to maintain pools of the two respective assets. Users can deposit these assets into the AMM, a process known as providing liquidity, in exchange for rewards. In exchange for providing liquidity to an AMM, users are given liquidity pool tokens. These liquidity pool tokens can then later be redeemed for the original deposited assets.

 An important thing to note is that the price of a liquidity pool token is not constant .

 Consider the following scenario. Our SOL-USDC constant product AMM has 1500 USDC and 10 SOL deposited, with 10 LP tokens minted. This means each LP token can be redeemed for 150 USDC and 1 SOL:

 1500 Â USDC 10 = 150 Â USDC 10 Â SOL 10 = 1 Â SOL \frac{1500\text{ USDC}}{10} = 150\text{ USDC}\\
\frac{10\text{ SOL}}{10} = 1\text{ SOL} 10 1500 Â USDC â = 150 Â USDC 10 10 Â SOL â = 1 Â SOL 
 Assuming the price of SOL is $150, the oracle would then calculate that each LP token can be redeemed for:

 150 Â USDC + 1 Â SOL = $ 150 + $ 150 = $ 300 150\text{ USDC} + 1\text{ SOL} = \text{\$}150 + \text{\$}150 = \text{\$}300 150 Â USDC + 1 Â SOL = $ 150 + $ 150 = $ 300 
 For a constant product AMM, a normal swap of 1 SOL for USDC would then return approximately 150 USDC.

 However, if someone swaps in 1500 USDC worth of SOL, the AMM will have 3000 USDC and 5 SOL, because they drove up the price of SOL in this pool.

 Itâs easy to confirm that this maintains the constant product invariant:

 3000 Ã 5 = 15000 = 1500 Ã 10 3000 \times 5 = 15000 = 1500 \times 10 3000 Ã 5 = 15000 = 1500 Ã 10 
 Letâs calculate the value of a single LP token now. For simplicity, letâs assume that the AMM doesnât take any fees.

 Similar to the math previously, each LP token can now be redeemed for:

 3000 Â USDC 10 = 300 Â USDC 5 Â SOL 10 = 0.5 Â SOL \frac{3000\text{ USDC}}{10} = 300\text{ USDC}\\
\frac{5\text{ SOL}}{10} = 0.5\text{ SOL} 10 3000 Â USDC â = 300 Â USDC 10 5 Â SOL â = 0.5 Â SOL 
 The value of the LP token is now:

 300 Â USDC + 0.5 Â SOL = $ 300 + $ 75 = $ 375 300\text{ USDC} + 0.5\text{ SOL} = \text{\$}300 + \text{\$}75 = \text{\$}375 300 Â USDC + 0.5 Â SOL = $ 300 + $ 75 = $ 375 
 Anyone who owns an LP token for this pool has effectively gained $75! 1 

 Important Constant product doesnât mean constant value.

 Note (Maximizing yields) Liquidity pool tokens are also an interesting example of how DeFi focuses on maximizing yields. Many lending protocols allow users to deposit LP tokens as collateral, and gain liquidity mining rewards along with interest on top of the normal liquidity pool yields. However, the extra complexity added by using liquidity pool tokens can easily lead to security problems.

## Oracles 

 On Solana, many platforms (leveraged farming, lending, perps, etc.) rely on oracles to determine the true value of an asset. When oracles misreport prices, this can result in stolen funds or insolvency of their respective protocols.

 Most oracle values are compiled from a variety of onchain and offchain sources. However, liquidity pool tokens by nature have a single point of failure: calculating how many backing tokens an LP token can be redeemed for, which is based off the token balance of the relevant liquidity pool.

 One such oracle is Switchboard, which is used by many popular lending protocols. Internally, Switchboard sends a GET request to the respective swap protocolâs API every minute, and directly pushes that price onchain.

 For example, the Switchboard task configuration for the price of stSOL on Raydium:

```

```
 1

 { 

 2

 " tasks " : [ 

 3

 { 

 4

 " httpTask " : { 

 5

 " url " : "https://api.raydium.io/pairs" 

 6

 } 

 7

 }, 

 8

 { 

 9

 " jsonParseTask " : { 

 10

 " path " : "$[?(@.name == 'stSOL-USDC')].price" 

 11

 } 

 12

 } 

 13

 ] 

 14

 } 

```

```

 The Raydium API calculates liquidity pool token values by pulling token balances from the respective AMM onchain. In other words, Switchboardâs oracle was directly reflecting the onchain state .

## Exploitation 

 Putting this all together, we start to see something suspicious. Pricing of liquidity pool tokens relies directly on onchain state, which can be easily manipulated.

 Recall previously that by swapping a large amount into a given AMM, we are able to change the global price for that AMMâs liquidity pool token.

 This transaction can be executed right before an oracle update. Alternatively, an attacker could lock the AMM by spamming transactions to effectively deny usage of the AMM to prevent arbitrage until the oracle updates.

 With our previous example, we manipulated the price of a liquidity pool token from $300 to $375. As a more extreme example, consider a transaction of 998500 USDC. After such a swap, the AMM will have 1 million USDC and 0.015 SOL. The oracle would report a value of over $100,000 per token:

 1000000 Â USDC + 0.015 Â SOL = $ 100000.225 1000000\text{ USDC} + 0.015\text{ SOL} = \text{\$}100000.225 1000000 Â USDC + 0.015 Â SOL = $ 100000.225 
 Now letâs explore how this manipulation can be used to steal funds.

## Lending 

 Lending is the simplest to exploit. By holding and manipulating the liquidity pool token price, we are able to directly affect the value of our underlying collateral. We are then able to overborrow against this collateral, stealing money from the lending protocol.

 More specifically, consider the following process:

- Manipulate price by swapping a large amount in the AMM.

- The oracle updates, and the liquidity pool token is now overvalued.

- Sell/buy back all the tokens to move the AMM price to a sane value.

- Mint liquidity pool tokens, deposit them as collateral, and borrow against that overvalued collateral.

- The oracle gets updated.

- Get liquidated by the lending protocol, but keep the borrowed assets.

 As a more concrete example, consider if an attacker spoofed the LP token price to $100,000,000, which was then uploaded to the oracle feed. After the oracle update, the attacker could move the LP token price back to a sane value such as $100. They would then be able to mint LP tokens for $100 each.

 Because the oracle prices are cached, the lending protocol mistakenly believes each LP token is worth $100,000,000. If the attacker deposited 1 LP token, they could then borrow against $100,000,000 of collateral, even though the real value of their deposits is only $100. For example, if the LTV of the lending protocol is 75%, they would be able to borrow $75,000,000 worth of tokens.

 After the price updates theyâll get liquidated, but keep the borrowed $75,000,000 of tokens. This gives a net profit of $74,999,900 minus any costs of the manipulation (for example, swap fees).

## Leveraged farming 

 Since you canât directly deposit liquidity pool tokens for leveraged farming, you must open a leveraged position, manipulate price, up your leverage (which increases liquidity that can be arbitraged because itâs at a bad price), sell off outside the farm, and set price back to normal.

 The steps are as follows:

- Manipulate price by swapping a large amount in the AMM.

- The oracle updates, and the liquidity pool token is now overvalued.

- Leverage higher valued collateral liquidity pool tokens to mint more liquidity pool tokens.

- This increases the liquidity in the pool â perform âarbitrageâ on the unbalanced liquidity pool.

- The oracle gets updated.

- Get liquidated, but keep profits from the âarbitrageâ.

 As a more concrete example, an attacker could open an LP position worth $100. They would then manipulate price so that their leveraged position is now worth $100,000,000.

 After borrowing $50,000,000 to lever up further and deposit more liquidity into the LP, they could sell at the inflated exchange rate outside, draining the $50,000,000 borrowed and any initial capital used to manipulate.

## Patch 

 This exploit is similar to some vulnerabilities which have happened on Ethereum involving flash loans and onchain oracles. To mitigate the issue, Alpha Finance introduced the concept of âfair pricingâ for constant product LP tokens.

 The concept is relatively simple. Instead of relying on the ratio of the tokens in the liquidity pool, compute what the ratio âshould beâ based on the relative price of the assets as determined by a trusted offchain oracle. This avoids using onchain data for pricing, which is susceptible to manipulation.

 For more details, we recommend reading the Alpha Finance article. An abridged computation can be found below:

 fairÂ LPÂ price = p b â expected_qty b + p a â expected_qty a qty = p b â ( amt a â amt b ) â ( p a / p b ) + p a â ( amt a â amt b ) â ( p b / p a ) qty = 2 amt a â amt b â p a â p b qty \text{fair LP price} = \frac{\text{p}_b \cdot \text{expected\_qty}_b + \text{p}_a \cdot \text{expected\_qty}_a}{\text{qty}}\\
= \frac{\text{p}_b \cdot \sqrt{(\text{amt}_a \cdot \text{amt}_b) \cdot (\text{p}_a/\text{p}_b)}
+ \text{p}_a \cdot \sqrt{(\text{amt}_a \cdot \text{amt}_b) \cdot (\text{p}_b/\text{p}_a)}}{\text{qty}} \\
= \frac{2\sqrt{\text{amt}_a \cdot \text{amt}_b \cdot \text{p}_a \cdot \text{p}_b}}{\text{qty}} fairÂ LPÂ price = qty p b â â expected_qty b â + p a â â expected_qty a â â = qty p b â â ( amt a â â amt b â ) â ( p a â / p b â ) â + p a â â ( amt a â â amt b â ) â ( p b â / p a â ) â â = qty 2 amt a â â amt b â â p a â â p b â â â 
 This concept also extends to stable curves, but there is no closed-form solution.

## Closing thoughts 

 While taken separately these components might seem innocuous, combined they allow for clever manipulation attacks. As with many security issues, a deep understanding of the underlying subsystem is required to discover potential inconsistencies.

 This attack has many similarities to the Warp Finance exploit on Ethereum, which also took advantage of LP tokens as collateral. DeFi developers should keep track of exploits everywhere, even ones that donât occur on their chain.

 We would also like to thank the following teams for their fast triage and response:

 Date 
 Event 

 1/02 
 Apricot is notified 

 1/02 
 Switchboard is notified 

 1/02 
 Apricot triages report 

 1/02 
 Switchboard triages report 

 1/06 
 Tulip is notified 

 1/07 
 Tulip releases patch 

 1/08 
 Port is notified 

 1/08 
 Port triages report 

 1/20 
 Switchboard releases patch (Port covered) 

 1/21 
 Apricot releases patch 

## Footnotes 

- 
 Assuming the value of USDC and SOL havenât changed. â©

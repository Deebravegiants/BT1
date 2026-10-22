# [H] Onyx Protocol - Rekt II exploit: Onyx Protocol, another Compound v2 fork that just can't catch a break, has been exploited again

## Summary
Severity: High
Target: Onyx Protocol - Rekt II
Loss: $3,800,000
Published: 09/25/2024
Source: https://rekt.news/onyx-protocol-rekt2
Type: rekt-postmortem

## Details
## Onyx Protocol - Rekt II

 Thursday, September 26, 2024 Onyx Protocol - Fork - REKT 

 read this article also in : 

 Onyx Protocol, another Compound v2 fork that just can't catch a break, has been exploited again. 

 This time, the damage tally stands at a cool $3.8 million, siphoned off by the same high-profile vulnerability that bit them late last year. 

 It's a rerun nobody asked for, featuring the usual suspects: a known bug, a newly added market, and a team seemingly allergic to learning from past mistakes.

 The exploit, executed with the precision of a seasoned chef following a recipe, drained a smorgasbord of assets including VUSD, XCN, DAI, WBTC, and USDT.

 Onyx finds itself in the unenviable "fool me twice" club, proving that in DeFi, lightning can indeed strike the same place twice - especially if you're holding a metal rod in a thunderstorm. 

 In the grand tapestry of DeFi disasters, is Onyx weaving a masterpiece or just tying itself in knots? 

 Credit: Cyvers , Onyx Protocol , Hacken , Peckshield

 In a plot twist surprising absolutely no one, Onyx Protocol decided to take "double or nothing" a bit too literally. 

 As crypto degens were busy arguing about the next meme coin or prepping for another conference, Cyvers played the role of party pooper:

 "Our system has detected suspicious transaction involving Onyx DAO on ETH chain! Total loss is around $3.8M." 

 Meanwhile, the Onyx team seemed to be practicing their ostrich impressions.

 4 hours after the exploit, they finally poked their heads out of the sand :

 "Onyx Protocol is aware of unusual activity on our platform and is currently reviewing third party post mortem examination data while conducting our own investigation." 

 But by then, the digital safe had long been cracked open, its contents scattered to the winds of the blockchain. 

 As blockchain detectives pieced together the digital crime scene, they found themselves watching a rerun of "Precision Manipulation: Onyx Edition." Same vulnerability, different day.

 Hacken, playing the role of DeFi's CSI team, laid out the attack blueprint . 

 Our intrepid hacker, clearly a fan of sequels, followed a script we've seen before: 

 Kick things off with a 2K ETH flash loan from Balancer. Because why use your own money when you can borrow someone else's?

 Play the ETH shell game: deposit 1,999.5 ETH into the oEther contract, while sneaking 0.5 ETH into a malicious contract cooked up just for the occasion.

 Use this custom contract to mint and redeem oETH in amounts so small, they'd make even a satoshi blush. We're talking 0.00000001 oETH here, folks. Because in DeFi, size doesn't always matter. 

 Rinse and repeat this minting and redeeming dance 56 times. Because if at first you don't succeed, try, try, try, try... (you get the idea) again. 

 Watch as the exchange rate goes haywire, proving once again that in DeFi, it's not about the size of your transaction, but how you use it.

 This precision manipulation attack exploited a vulnerability that's becoming all too familiar in the Compound V2 family reunion.

 The flaw? A hiccup in the asset's exchange rate calculation when there's low liquidity in a market. 

 It's as if Onyx left the door wide open, hung up a "Free Money" sign, and went on vacation. 

 Exploiter address: 
 0x680910cf5Fc9969A25Fd57e7896A14fF1E55F36B 

 Attack transaction: 
 0x46567c731c4f4f7e27c4ce591f0aebdeb2d9ae1038237a0134de7b13e63d8729 

 Attack Contract: 

 0xAE7d68b140Ed075E382e0A01d6c67ac675AFa223 

 But wait, there's more! Our enterprising hacker didn't stop there.

 Peckshield, playing the role of DeFi's Sherlock Holmes, uncovered another skeleton in Onyx's closet .

 The attacker also exploited a flaw in the NFTLiquidation contract, which failed to properly validate user input. 

 This allowed them to inflate the self-liquidation reward amount, essentially giving them a blank check drawn on Onyx's account. 

 The end result? A smorgasbord of stolen assets according to Peckshield : 

 4.1M VUSD

 7.35M XCN

 5K DAI

 0.23 WBTC

 50K USDT

 All in all, a $3.8M payday for our hacker, and another painful lesson for Onyx Protocol. 

 One they've already learned... and apparently forgotten. 

 Speaking of forgetting, in the Pokémon world, Onix evolves into Steelix, becoming stronger and more resilient.

 But in DeFi, Onyx Protocol seems stuck in a permanent state of vulnerability, as if it used an Everstone on itself. 

 No matter how many times it gets hit by super-effective exploits, it never learns a new move. 

 It's less "Rock Throw" and more "Self-Destruct" at this point.

 CertiK audited Onyx back in January 2022, and since then? Radio silence. No updates, no follow-ups, nada. At least publicly.

 It's as if Onyx thinks smart contracts are like fine wine - leave them alone and they'll get better with age. Spoiler alert: they don't.

 Meanwhile, Onyx decided to play Russian roulette with their protocol, adding a VUSD market via governance proposal. 

 Because who needs a fresh audit when you're introducing new markets, right?

 Apparently, Onyx's idea of spring cleaning is sweeping old vulnerabilities under the rug while rolling out the red carpet for new ones.

 They didn't just skip a few steps; they took the express elevator to Rekt City, bypassing all the safety floors along the way. 

 In a world where "move fast and break things" meets "copy-paste and pray," is DeFi innovation outpacing common sense, or is common sense just taking a very, very long lunch break? 

 If this story gives you a sense of déjà vu, you're not alone. 

 We've been here before, folks. In our previous coverage of Onyx's misadventures, we highlighted a crucial point: while Certik did their audit dance, the real vulnerability lurks in the market conditions, not just the codebase. 

 Remember the golden rule of Compound V2 forks? Empty markets are like catnip for hackers.

 Launching new markets should be handled with the care of a bomb disposal expert, not a "yolo and hope for the best" attitude.

 After the Hundred Finance sequel hack, Hexagate dropped some wisdom : 

 "Mint some cTokens, burn them, and make sure the total supply never hits zero. It's like DeFi's version of always leaving one cookie in the jar." 

 But did Onyx listen?

 Apparently, their memory is shorter than a goldfish's, and their learning curve flatter than a pancake.

 In the grand theater of DeFi, Onyx has managed to turn "once bitten, twice shy" into "twice bitten, still clueless." 

 As the curtain falls on this repeat performance, one can't help but wonder: in a space where code is law, who's writing the constitution? And more importantly, who's bothering to read it? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

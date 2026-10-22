# [H] Platypus Finance exploit: Avalanche-based Platypus Finance lost $8.5M to a flash loan attack on its new stablecoin

## Summary
Severity: High
Target: Platypus Finance
Loss: $8,500,000
Published: 02/17/2023
Source: https://rekt.news/platypus-finance-rekt
Type: rekt-postmortem

## Details
## Platypus Finance - REKT

 Thursday, February 16, 2023 Platypus Finance - Avalanche - REKT 

 read this article also in : zh 

 Evolution works in mysterious ways. 

 Avalanche-based Platypus Finance lost $8.5M to a flash loan attack on its new stablecoin. 

 A highly-specialised creature may be well suited to its own habitat, but Platypus’ attempts to adapt have ended up dead in the water. 

 Adding to its existing stableswap AMM platform, Platypus recently launched its own stablecoin, USP. However, just 10 days after launch, the new mechanism was attacked, depegging USP and leaving it heavily undercollateralised.

 The Platypus team announced the attack:

 Dear Community,

 We regret to inform you that our protocol was hacked recently, and the attacker took advantage of a flaw in our USP solvency check mechanism. They used a flashloan to exploit a logic error in the USP solvency check mechanism in the contract holding the collateral.

 According to a recent announcement on the launch, USP “ provides an extra layer of protection from the volatility that other stablecoins may experience ”.

 A statement worthy of a Darwin award? 

 Credit: Daniel Von Fange , Peckshield 

 The exploit took advantage of a faulty check mechanism when withdrawing collateral. 

 The attacker first took a flash loan of 44M USDC which was deposited into Platypus. The resulting LP tokens were then used as collateral to borrow 41.7M USP.

 The emergencyWithdraw() function only checks whether the user’s position is currently solvent, but neglects to first check against any the effect of any borrowed funds. This allows the attacker to withdraw the supplied collateral while keeping the borrowed USP.

 The collateral was then withdrawn to repay the flash loan, and the USP was swapped via Platypus pools, draining the existing liquidity of other stables (USDC, USDT, DAI, BUSD, etc.). 

 Attacker’s address: 0xeff003d64046a6f521ba31f39405cb720e953958 

 Attack tx: 0x1266a937… 

 Attack contract: 0x67afdd6489d40a01dae65f709367e1b1d18a5322/ 

 The hack has left USP depegged by over 50% as the attacker swapped the USP for other stables. The stolen $8.5M remain in the hacker’s contract , of which, $1.5M of stolen USDT has been blacklisted . 

 The rather simple vulnerability, combined with the loot being left ( or possibly trapped ) as freezable, centralised stables suggests this heist may have been pulled off by a relatively inexperienced amateur.

 Why not swap to a less controlled asset? Or bridge the funds and send them to Tornado? 

 As it turns out, OPSEC is not this hacker’s strong suit. 

 After just a few hours, fellow platypus ZachXBT managed to identify the culprit via their ENS address, linked to the exploiter’s transaction history. The same alias was used for now-deleted Twitter and Instagram accounts. The Platypus team have since appealed to the doxxed exploiter:

 We're in the process of setting up a bounty & encourage the hacker to reach out to us. We also welcome anyone with useful information to come forward to us.

 Safety in numbers… 

 Just like the Platypus itself, DeFi is a strange and unique beast. 

 A hybrid species born of cypherpunk hackers and finance bros, every protocol must speedrun their way through natural selection. 

 It’s a jungle out there…

 …and, as ever, it’s survival of the fittest. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [C] JPEG'd incident: The NFT lending platform JPEG'd was hacked, and JPEG tokens fell by 40% in a short period of time, with a loss of at least about $

## Summary
Severity: Critical
Target: JPEG'd
Loss: $ 11,363,266
Attack method: Reentrancy Attack
Published: 2023-07-30
Source: https://www.panewslab.com/zh/sqarticledetails/670e3s1g.html
Type: slowmist-incident

## Details
The NFT lending platform JPEG'd was hacked, and JPEG tokens fell by 40% in a short period of time, with a loss of at least about $10 million. The root cause is re-entry. When the attacker calls the remove_liquidity function to remove liquidity, he adds liquidity by re-entering the add liquidity function. Because the balance update is before re-entering the add_liquidity function, the price calculation is wrong. JPEG'd tweeted that the PETH-ETH curve pool was attacked. The vault contract that allows NFTs to be borrowed is safe and still functioning. NFT and treasury fund security. The JPEG'd contract has not been hacked and is safe. On August 5, JPEG'd tweeted that the DAO multi-signature address confirmed receipt of 5494.4 WETH, and the address owner who recovered funds from the pETH vulnerability received a 10% white hat bounty, which is 610.6 WETH.

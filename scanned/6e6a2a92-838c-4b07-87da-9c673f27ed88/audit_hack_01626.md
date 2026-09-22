# [M] VETH incident: Coingecko researcher Daryllautk tweeted that VETH suffered a hacker attack on the decentralized exchange Uniswap. The hacker stole

## Summary
Severity: Medium
Target: VETH
Loss: $ 900,000
Attack method: Contract Vulnerability
Published: 2020-07-01
Source: https://www.tuoniaox.com/newsflash/p-447988.html
Type: slowmist-incident

## Details
Coingecko researcher Daryllautk tweeted that VETH suffered a hacker attack on the decentralized exchange Uniswap. The hacker stole 919,299 VETH (worth $900,000) using only 0.9ETH. After the attack, VETH officially stated that the contract was used by the UX improvement it placed in transferForm(), which was their fault. They will redeploy vether4 and will compensate all affected Uniswap pledgers. This attack mainly uses the visibility of the changeExcluded function in the contract to be external and there is no permission restriction. The user can directly make external calls to create the necessary conditions for the attack.

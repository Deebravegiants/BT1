# [M] Quixotic incident: Quiuixotic, the largest NFT platform in the Optimism ecosystem, has a serious vulnerability, and a large number of user assets hav

## Summary
Severity: Medium
Target: Quixotic
Loss: 220,000 OP
Attack method: Contract Vulnerability
Published: 2022-07-01
Source: https://www.defidaonews.com/article/6762124
Type: slowmist-incident

## Details
Quiuixotic, the largest NFT platform in the Optimism ecosystem, has a serious vulnerability, and a large number of user assets have been stolen. Users who have traded on this market should cancel their authorization as soon as possible. According to SlowMist analysis, only the sell order is checked in the fillSellOrder function of the market contract, and the buyer's buy order is not checked. Therefore, the attacker first creates an arbitrary NFT contract, calls the fillSellOrder function to generate a sell order, and passes the buyer parameter as the victim's address and the paymentERC20 parameter as the token address to be stolen, then the user who is authorized to the market contract can be transferred. Tokens are transferred for profit.

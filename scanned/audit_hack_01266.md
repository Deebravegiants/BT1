# [C] whaleswap.finance incident: The whaleswap.finance project was attacked, and at least 5946 BUSD and 5964 USDT were lost. The reason may be that there is a prob

## Summary
Severity: Critical
Target: whaleswap.finance
Loss: 5946 BUSD+5964 USDT
Attack method: K value verification vulnerability
Published: 2022-06-21
Source: https://www.panewslab.com/zh/sqarticledetails/xa9zc04d.html
Type: slowmist-incident

## Details
The whaleswap.finance project was attacked, and at least 5946 BUSD and 5964 USDT were lost. The reason may be that there is a problem with the K value verification of the whaleswap.finance Pair contract. Whenever the user exchanges, there is a problem with the parameter magnitude passed in the K value verification, which causes the K value verification to fail. The attacker first borrows a BSC-USD through a flash loan, and then returns the flash loan when the K value verification parameter is on the order of 10000^4. The parameter verification level used in the K value verification is 10000^2, which causes the K verification to fail.

# [M] First ERC4626 deposit can break share cal-

## Summary
Severity: Medium
Contest weight: 0.1907
Dataset id: 17726
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The first depositor of an ERC4626 vault can maliciously manipulate the share price by depositing the lowest possible amount (1 wei) of liquidity and then artificially inflating ERC4626.totalAssets. This can inflate the base share price as high as 1:1e18 early on, which force all subsequence deposit to use this share price as a base and worst case, due to rounding down, if this malicious initial deposit front-run someone else depositing, this depositor will receive 0 shares and lost his deposited assets. Given a vault with DAI as the underlying asset: Alice (attacker) deposits initial liquidity of 1 wei DAI via deposit() Alice receives 1e18 (1 wei) vault shares Alice transfers 1 ether of DAI via transfer() to the vault to artificially inflate the asset balance without minting new shares. The asset balance is now 1 ether + 1 wei DAI -> vault share price is now very high (= 1000000000000000000001 wei ~ 1000 * 1e18) Bob (victim) deposits 100 ether DAI Bob receives 0 shares Bob receives 0 shares due to a precision issue. His deposited funds are lost. The shares are calculated as following return supply == 0 ? assets : assets.mulDivDown(supply, totalAssets()); In case of a very high share price, due to totalAssets() > assets * supply, shares will be 0. ERC4626 vault share price can be maliciously inflated on the initial deposit, leading to the next depositor losing assets due to precision issues.

## Recommendation
This is a well-known issue, Uniswap and other protocols had similar issues when supply == 0.

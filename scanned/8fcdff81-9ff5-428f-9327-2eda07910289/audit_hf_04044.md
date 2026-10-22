# [H] Clearinghouse.sol#claimDefaulted()

## Summary
Severity: High
Contest weight: 0.2347
Dataset id: 20481
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside claimDefaulted on the last line we call MINTR.burnOhm which in turn calls OHM.burnFrom. The docs for MINTR.burnFrom state: "Burn OHM from an address. Must have approval.". We can confirm that this is the case when looking at OHM source code and it's burnFrom. I found 2 OHM tokens that are currently deployed on mainnet, so I'm linking both their addresses: https://etherscan.io/token/0x383518188c0c6d7730d91b2c03a03c837814a899#code, https://etherscan.io/token/0x64a a3364f17a4d01c6f1751fd97c2bd3d7e7f1d5#code. Both addresses use the same burnFrom logic and in both cases they require an allowance. Nowhere in the contract do we approve the MINTR to handle OHM tokens in the name of Clearinghouse, in fact OHM isn't even specified in Clearinghouse. incorrectly. When burnFrom gets called MockOhm calls the inherited _burn function, which burns tokens from msg.sender. The mock doesn't represent how the real OHM.burnFrom works. Claimdefault will always revert.

## Recommendation
Add a variable ohm which will be the OHM address and approve the necessary tokens to the MINTR before calling MINTR.burnOhm.

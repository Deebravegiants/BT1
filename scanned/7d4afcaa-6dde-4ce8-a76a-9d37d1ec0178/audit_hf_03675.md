# [H] Price of voltGNS share is calculated incorrectly

## Summary
Severity: High
Contest weight: 0.3041
Dataset id: 19768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Forget to deduct the boostedGNS when calculating price
The price of voltGNS is updated whenever the function voltGNS.swapToGNS() is called.
The function firstly calculates the totalStaked which is amount of gns staking in gnsVault plus with amount of gns which was swapped from pendingDai. Then the price will be determined by dividing totalStaked with totalSupply() of the vault.
At the first glance, this formula seem right when calculating the price using the total underlying assets and the total shares supply. So it means that if I withdraw all the totalSupply shares, I can receive all the totalStaked. Unfortunately this won't be happened because of the boostedGNS. The boostedGNS is amount of gns which is deposited by the owner and no share will be minted for the him. Furthermore this amount can be deposited / withdrew at anytime whenever the owner wants.
This boostedGNS mechanism can lead to the big issue for the VoltaVault contract which uses the voltGNS as collateral. When the owner calls unboostGNS(), it can make the voltGNS.price() lose a lot of value. That will make the big liquidation events occured for a lot of users without noticing them.
The price of a token should depend on the fluctuation of the market, and should not depend on the single individual like owner. Malicious owner can abuse this to make profit.
When owner calls unboostGNS() can incur a immediate liquidation for users without their preparation.

## Recommendation
Deducting the boostedGNS out of totalStaked when calculating the price.

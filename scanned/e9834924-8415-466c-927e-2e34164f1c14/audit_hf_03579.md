# [M] TRH-2 | The Balance Of Any Disabled Token Can Get Hijacked

## Summary
Severity: Medium
Contest weight: 0.1167
Dataset id: 19558
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Any asset, that gets disabled will have it's balance hijacked due to a lack of access control on claim(). Function claim() calls accrue(_tokenRewards[token]), which is a private function only also called in accrue(). This function updates the current index of each epoch on the token based on the totalSupply of custodian shares at the moment. Due to the asset not being in the _rewardTokens anymore, it does not get its index updated upon a user change. Consequently claim() is prone to a Portfolio share inflation attack that steals the whole balance of the said reward token. This can be achieved by depositing a large amount of the asset, calling claim(), which updates the accrued for that token based on the now inflated balance of shares and then transfers an inflated portion to the user.

## Recommendation
Put only active token access control on claim().

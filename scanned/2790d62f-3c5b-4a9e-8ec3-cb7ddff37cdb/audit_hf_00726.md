# [H] H-07 | LPs Can Game Liquidations Via mintUsd

## Summary
Severity: High
Contest weight: 0.3731
Dataset id: 2277
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When ﬂagging a position for liquidation all of the account’s collateral is seized which will immediately reduce the reportedDebt. However the position’s unrealized losses are still present in the reportedDebt before the liquidatePosition function has been called. The account’s collateral that was seized is intended to cover the position’s losses, however upon a debt distribution and rebalancing of the pool the backing LPs debt will be decreased by the collateral removed but not yet increased by the liquidation of the position that is in a loss. SIP-366, Asynchronous Delegation, aims to address a scenario in which LPs would be able to speciﬁcally target this intermediate liquidation mis-accounting in order to undelegate while the debt of their position has been deﬂated. This addresses the vector where LPs would undelegate from the pool, however LPs may still mintUsd while they have this artiﬁcially lowered debt. This way an LP could mintUsd up to the c-ratio while their debt is suppressed, and then once the BFP account is liquidated the LPs position would be immediately under the c-ratio by a stepwise, and potentially signiﬁcant, amount. In some cases LPs may be able to mint more sUSD than they would lose from liquidation. As a result, the LP forces others in the vault to take on socialized debt and can even potentially make keeper fee proﬁts from triggering the BFP liquidation and their own V3 liquidation in the same block. Additionally, even with SIP-366 implemented LPs could frontrun the processIntentToDelegateCollateral function call to trigger a ﬂagging of a position. Or process their own intent before ﬂagging a position in BFP. Though these actions are not as guaranteed.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs/pull/5/files

## Recommendation
Ensure that c-ratios in the V3 core system are assigned such that it would not be possible for an LP to gain a net proﬁt from:
1. Flagging a large position in the BFP market, realizing the collateral + not-yet-reduced losses gain + ﬂag reward
2. Liquidating the BFP position, realizing the liquidation reward
3. Liquidating the BFP position, realizing the liquidation reward
4. Liquidating their now unhealthy V3 core position + any other accounts in the same vault that would be made unhealthy, realizing the liquidation reward

# [M] Liquidation frontrunning can prevent debt re-

## Summary
Severity: Medium
Contest weight: 0.2506
Dataset id: 20011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During a period of time that the PauseRouter is in use, the valuations of a user's debt and collateral may make them subject to liquidation. But, in the first block after the normal Router is restored, MEV bots can preempt any transactions that could prevent the liquidation (e.g. repayment or adding collateral).
Pausing and unpausing the router is performed via a call to the active router's inherited UUPSUpgradeable.upgradeTo() (or upgradeToAndCall()) function and supplying the address of the next router contract, which calls GovernanceAction._authorizeUpgrade() and then ERC1967Upgrade._upgradeToAndCallSecure() which ends with ERC1967Upgrade._upgradeTo() switching the implementation address to realize the desired change. Pausing may be performed by either the owner or the pause guardian role. Only the owner can unpause the system.
Notional has forked governance logic from Compound. In Compound, "Importantly, the pauseGuardian does not have the ability to prevent users from exiting their positions by calling redeem or repayBorrow". However, in Notional this is not true.
The PauseRouter does not delegate account action functions that would allow debt repayment. As such, without recourse to avoid it, user debt positions may become liquidatable during a pause.
MEV bots are able to use view functions to monitor account health during a pause. So, while they may actively detect and frontrun debt repayment transactions upon system unpausing, it is not required. The normal operation of liquidators bots can have the same effect.
by system configuration at the discretion of the owner or pause guardian and enabling it would pose additional liquidation risk to users.) The frontrunning vulnerability is present even if liquidations are not enabled during a pause.
By frontrunning any debt repayment (or collateral deposit) attempts after unpausing the router, MEV bots can unfairly liquidate all debt positions that became eligible for liquidation during the pause. This causes loss of funds to all affected users.

## Recommendation
If liquidation is not allowed during a pause, add a grace period after unpausing during which liquidation remains blocked to allow users to avoid unfair liquidation by repaying debt or supplying additional collateral.

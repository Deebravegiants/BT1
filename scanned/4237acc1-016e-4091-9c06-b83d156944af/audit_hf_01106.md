# [M] Changing Transmuters for an Alchemist would harm creditors

## Summary
Severity: Medium
Contest weight: 0.1181
Dataset id: 4240
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Alchemist allows swapping out Transmuters through the setTransmuter() function.
However, sunsetting a Transmuter without simultaneously sunsetting (all) its Alchemist(s) would be very difficult to do in a way that does not harm creditors with debt tokens in the Transmuter.
The Transmuter relies on its privileged access to it's Alchemist(s) in order to redeem yield tokens to pay back creditors. In the event that it loses this privilege, redemptions will fail for any position that the Transmuter cannot cover. The value in the Transmuter would likely be drained by new or old creditors entering and exiting positions until all yield tokens have been siphoned off.

## Recommendation
Only sunset a Transmuter, which is in some way buggy and absolutely needs swapping out. Make it possible to lower the deposit cap arbitrarily, even to 0, to block new deposits (currently, it cannot be lowered below the current totalLocked in the Transmuter). Make the Transmuter creditors whole with emergency funds, if available.

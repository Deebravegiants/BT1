# [M] Wrong permissions on `reassignGlobalAdmin`

## Summary
Severity: Medium
Contest weight: 0.1016
Dataset id: 1141
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `Permissions.reassignGlobalAdmin` function is supposed to only be run with the `TIMELOCK_ROLE` role, see `onlyRole(TIMELOCK_ROLE, "Only timelock can assign roles")`.

However, the `TIMELOCK_ROLE` is not the admin of all the reassigned roles and the `revokeRole(role, oldAccount)` calls will fail as it requires the `ADMIN_ROLE`.

## Recommendation
The idea might have been that only the `TIMELOCK` should be able to call this function, and usually it is also an admin, but the function strictly does not work if the caller _only_ has the `TIMELOCK` roll and will revert in this case. Maybe governance decided to remove the admin role from the Timelock, which makes it impossible to call `reassignGlobalAdmin` anymore as both the timelock and admin are locked out.

The warden has identified a flaw in the roles implementation, while the system seems to work when the timelock has multiple roles, the name of the roles implies a different functionality than what can actually be done. The sponsor confirms. While I believe the impact in the demo setup to be fairly minor, because the finding shows a flow in the role setup, and the sponsor confirmed, I agree with medium severity

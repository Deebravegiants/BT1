# [M] 6.4 Missing Shutdown Logic

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Each ConvexStakingWrapper smart contract can be shut down by the owner so that accounting of the
rewards stops and users are only able to withdraw their shares of the pool. Rewards will not be
accounted for anymore when moving wrapped tokens around because the _checkpoint() function
does not apply any logic when the isShutdown flag is set to true.

However, the _checkpointAndClaim() function does not have any such check for the flag, meaning
that users are still able to claim their rewards after the shutdown. Users could also still transfer the
wrapped tokens without the wrapper checkpointing it so an attacker could manipulate its balance to steal
some rewards.

Code corrected:

Both functions now implement the shutdown logic.

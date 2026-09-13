# [M] Filter Logic calls to gravity cosmos at client level to avoid reverts

## Summary
Severity: Medium
Source: https://github.com/althea-net/cosmos-gravity-bridge/blob/92d0e12cea813305e6472851beeb80bd2eaf858d/orchestrator/ethereum_gravity/src/logic_call.rs#L187
Type: audit-issue

## Details
# Handle

hack3r-0m


# Vulnerability details

https://github.com/althea-net/cosmos-gravity-bridge/blob/92d0e12cea813305e6472851beeb80bd2eaf858d/orchestrator/ethereum_gravity/src/logic_call.rs#L187

Add a check for `call.logic_contract_address` to make sure it is not the same as gravity contract to avoid panics from the orchestrator (by failing gas estimations)

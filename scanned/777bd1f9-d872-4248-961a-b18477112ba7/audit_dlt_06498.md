# [M] LM_PC_KPIRewarder_v1.sol#postAssertion() - Protocol assumes that `asserter` pays for the bond, but he doesn't

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/64
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @EgisSec
**Submission hash (on-chain):** 0x9bbb663d2c480d1d8251784764147d551a2f8bd8fca2294d5c03b0d5311c2b5f
**Severity:** medium

**Description:**
**Description**\
`postAssertion` is called when someone wants to create an assertion for `targetKPI`.

```sol
function postAssertion(
        bytes32 dataId,
        uint assertedValue,
        address asserter,
        uint targetKPI
    ) public onlyModuleRole(ASSERTER_ROLE) returns (bytes32 assertionId) {
        if (assertionPending) {
            revert Module__LM_PC_KPIRewarder_v1__UnresolvedAssertionExists();
        }

        //--------------------------------------------------------------------------
        // Input Validation

        //  If the asserter is the Module itself, we need to ensure the token paid for bond is different than the one used for staking, since it could mess with the balances
        if (
            asserter == address(this)
                && address(defaultCurrency) == stakingToken
        ) {
            revert
                Module__LM_PC_KPIRewarder_v1__ModuleCannotUseStakingTokenAsBond();
        }

        // Make sure that we are targeting an existing KPI
        if (KPICounter == 0 || targetKPI >= KPICounter) {
            revert Module__LM_PC_KPIRewarder_v1__InvalidKPINumber();
        }

        //--------------------------------------------------------------------------
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/64_

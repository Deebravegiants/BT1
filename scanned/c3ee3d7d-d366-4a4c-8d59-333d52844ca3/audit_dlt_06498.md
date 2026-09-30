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
        // Staking Queue Management

        for (uint i = 0; i < stakingQueue.length; i++) {
            address user = stakingQueue[i];
            _stake(user, stakingQueueAmounts[user]);
            totalQueuedFunds -= stakingQueueAmounts[user];
            stakingQueueAmounts[user] = 0;
        }

        delete stakingQueue; // reset the queue

        //--------------------------------------------------------------------------
        // Assertion Posting

        assertionId = assertDataFor(dataId, bytes32(assertedValue), asserter);
        assertionConfig[assertionId] = RewardRoundConfiguration(
            block.timestamp, assertedValue, targetKPI, false
        );

        emit RewardRoundConfigured(
            assertionId, block.timestamp, assertedValue, targetKPI
        );

        assertionPending = true;

        // (return assertionId)
    }
```

The function also takes an `asserter` argument, which the protocol describes as:
>  @dev about the asserter address: any address can be set as asserter, it will be expected to pay for the bond on posting.
    The bond tokens can also be deposited in the Module and used to pay for itself, but ONLY if the bond token is different from the one being used for staking.
    If the asserter is set to 0, whomever calls postAssertion will be paying the bond.

This is the comment above the actual function. The protocol assumes that whoever is set as `asserter` has to pay for the bond to OOv3.

This is incorrect, as if we take a look at `assertDataFor`.

```sol
  function assertDataFor(bytes32 dataId, bytes32 data, address asserter)
        public
        virtual
        onlyModuleRole(ASSERTER_ROLE)
        returns (bytes32 assertionId)
    {
        asserter = asserter == address(0) ? _msgSender() : asserter;
        defaultCurrency.safeTransferFrom(
            _msgSender(), address(this), defaultBond
        );
        defaultCurrency.safeIncreaseAllowance(address(oo), defaultBond);
        ...
```

You can see that `_msgSender()` always pays for the `defaultBond`, not the `asserter`.

Setting the `asserter` address will only affect who receives the bond when an assertion is settled or in some cases when it's disputed. It's now however used to pay for the actual bond, `msgSender()` always pays for the bond, i.e whoever called `poastAssertion`.

This breaks an assumption of the protocol that the passed `asserter` address pays for the bond and also breaks the assumption that if `asserter == address(this)` than the actual `LM_PC_KPIRewarder_v1` will pay for the bond, effectively making the `depositFeeFunds` useless, as it's impossible for `address(this)` to pay for the bond, as `_msgSender()` is always forced to transfer `defaultBond` to `address(this)`.


**Attack Scenario**\

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

Rework `assertDataFor` so that it correctly transfers the bond from the `asserter` not `_msgSender()`.

If you want `address(this)` to be able to pay for the assertion himself, add an extra check if `asserter == address(this)` and check if the address has enough balance to cover the bond.

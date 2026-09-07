# [H] Anyone can become the admin  of StableSwapFactory at anytime

## Summary
Severity: High
Chain: Smart contract
Component: Thorn-protocol
Published: 2024-10-03
Source: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/1
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x41fa70ee15ad9f5be6daf33aa22deea9e547fd94b231e4d5b0f327098deb502d
**Severity:** high

**Description:**
**Description**\
Anyone can become the admin  of `StableSwapFactory.sol` at any time. The contract has an `initialize()` function which can be called by anyone at any time, infinite times with different args each time.  Thus, the `admin` and the other state variables can be changed with arbitrary values.

```solidity
     function initialize(
        IStableSwapLPFactory _LPFactory,
        IStableSwapDeployer _SwapTwoPoolDeployer,
        IStableSwapDeployer _SwapThreePoolDeployer,
        address _admin

     ) public  {//@audit-issue anyone can initialize the contract at anytime, infinite times
        LPFactory = _LPFactory;
        SwapTwoPoolDeployer = _SwapTwoPoolDeployer;
        SwapThreePoolDeployer = _SwapThreePoolDeployer;
        admin=_admin; <@anyone can become the admin at any time
     }
```

This is because the contract does not check if `initialize()` was called before.


**Attack Scenario**\
- Attacker calls `StableSwapFactory::initialize()` and becomes the admin of the contract, overriding the existing admin.
-  Now the attacker has access to all onlyAdmin functions in StableSwapFactory
    - he can create his own swap pairs with custom exchange fees and admin_fees
    - he can mint an infinite amount of `StableSwapLP `tokens. He can override the `SwapTwoPoolDeployer `address with his own, which returns his custom address that will become the minter of the LP contract.

```solidity
    function createSwapPair(
        address _tokenA,
        address _tokenB,
        uint256 _A,
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/1_

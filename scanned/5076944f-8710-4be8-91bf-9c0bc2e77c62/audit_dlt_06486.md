# [H] FM_BC_Bancor_Redeeming_VirtualSupply_v1.sol#transferOrchestratorToken() - The function doesn't take into account `projectCollateralFeeCollected` when the function is called

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-11
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/101
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @EgisSec
**Submission hash (on-chain):** 0xb60c57a1f3baa974f84745ee25e7e9df3925d3093116ea84c0b39bc4f2182bf5
**Severity:** high

**Description:**
**Description**\
All funding managers (FM for short) have `transferOrchestratorToken`, this is what allows the orchestrator to pull funds out of the FM's (FM for short).

Let's take a look at `FM_BC_Bancor_Redeeming_VirtualSupply_v1` implementation.

```solidity
function transferOrchestratorToken(address to, uint amount)
        external
        virtual
        onlyOrchestrator
    {
        __Module_orchestrator.fundingManager().token().safeTransfer(to, amount);

        emit TransferOrchestratorToken(to, amount);
    }
```

You can see that the function simply transfers the tokens to the `to` address and does nothing else.

`FM_BC_Bancor_Redeeming_VirtualSupply_v1` implements `RedeemingBondingCurveBase_v1`, which in itself implements `BondingCurveBase_v1`.

`BondingCurveBase_v1` holds the `_buyOrder` function and `RedeemingBondingCurveBase_v1` holds the `_sellOrder` function.

Both functions implement quite a lot of fees, which are in the form of collateral and issuance tokens.

The collateral is transferred outright and the issuance is minted, but there is an exception.

There is also a `workflowFeeAmount`, which is based on the `buyFee` and `sellFee` respectively. This is in the form of collateral (the funding manager's token).

This fee isn't transfered outright, it's stored in `projectCollateralFeeCollected `.
```solidity
// Add workflow fee if applicable
        if (workflowFeeAmount > 0) {
            projectCollateralFeeCollected += workflowFeeAmount;
        }
```

Which can then later be transfered out of the contract with `withdrawProjectCollateralFee`.

```solidity
 function withdrawProjectCollateralFee(address _receiver, uint _amount)
        public
        virtual
        validReceiver(_receiver)
        onlyOrchestratorAdmin
    {
        if (_amount > projectCollateralFeeCollected) {
            revert Module__BondingCurveBase__InvalidWithdrawAmount();
        }

        projectCollateralFeeCollected -= _amount;

        __Module_orchestrator.fundingManager().token().safeTransfer(
            _receiver, _amount
        );

        emit ProjectCollateralFeeWithdrawn(_receiver, _amount);
    }
```

Knowing this, if we go back to `transferOrchestratorToken` you'll notice that there aren't any checks for `projectCollateralFeeCollected`, meaning that when a module is in need of funds and calls the orchestrator, who in turn calls `transferOrchestratorToken`, tokens that are meant to be withdrawn as fees will be transferred as well.

Because of this, the protocol will lose their entire fees that were accumulated.

Currently the only place where `transferOrchestratorToken` is called is in `ERC20PaymentClientBase_v1.sol#_ensureTokenBalance`, which is inherited from all of the logic modules.

**Attack Scenario**\

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

Take into account `projectCollateralFeeCollected` when the transfering tokens out of the funding manager.

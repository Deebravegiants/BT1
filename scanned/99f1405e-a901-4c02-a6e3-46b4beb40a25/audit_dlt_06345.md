# [H] There is no way to withdraw tokens from Bfx when deposited from BfxVault via Treasurer

## Summary
Severity: High
Chain: Smart contract
Component: Blast-Futures-Exchange
Published: 2024-02-05
Source: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/8
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x6f8a91f9055b01793644245a33f71beb6bcf27eccbc4a9a7d58eab1f9c12d260
**Severity:** high

**Description:**
**Description**

The protocol seems to work mainly off-chain. Deposits are done on-chain and after deposits, events are emitted with (depositdId,msg.sender,amount), this is same for staking, only depositId became StakeId. So the withdrawals are using those events and are done off-chain, at least thats what code is telling us (I don't want to assume there is no way for withdrawing tokens obviously.) So in order to withdraw from the protocol off-chain system will be used. Assumingly to do that users need to provide their depositId/stakeId in UX and after off-chain system checked that event's (which emitted during deposit) msg.sender is the same as the requester of withdrawal(otherwise it would be possible to steal anyone's funds so this check is not optimal), and then will proceed with starting withdrawing process. Unfortunately in "BfxVault.sol", there is a function "makeDeposit()" which basically deposit tokens that are available in contract to "Bfx.sol" via Bfx's deposit() function. But since this contract can not possibly interact with the UX to start the withdraw process. It won't be able to withdraw tokens and funds will be stuck.

One side note, this is also case for all contracts (that are not EOA), it is important to document this thoroughly so that users won't lose funds.

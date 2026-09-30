# [M] User can DOS its own ingresso transactions by

## Summary
Severity: Medium
Contest weight: 0.4613
Dataset id: 22451
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
User can ERC20.approve deposit amount to ciao address, create deposit request via off-chain app, but then front-running ingresso transaction with removal or reduction of approved amount to ciao address. This will cause the deposit and whole ingresso transaction to revert. This can be repeated again (simply increase approved amount again, possibly re-creating off-chain deposit request again).
Such user behavior will cause lots of reverted transactions (with wasted/lost gas by operator), disruption of the protocol service to the other users (due to failed transactions) and moreover will allow user to selectively censor ingresso transactions (allowing what he "likes" to proceed and what he doesn't like to revert).
Ciao.deposit uses ERC20 transferFrom to transfer funds from the user:
// Pull resources from sender to this contract
SafeTransferLib.safeTransferFrom(
ERC20(asset),
account,
address(this),
quantity
);
This is also called from OrderDispatch.deposit action:
ICiao(Commons.ciao(address(addressManifest))).deposit(
depo.account,
depo.subAccountId,
depo.quantity,
depo.asset
);
This means that user must first approve Ciao address to spend this amount of asset. This should be checked by off-chain app before it sends ingresso transaction with deposit.
However, the user can front-run this transaction and reduce approved amount to cause ingresso transaction revert. This will waste operator's gas, and since ingresso might include the other transactions as well, this will also cause disruption to protocol service.
Alternatively, especially in L2 networks with no mempool - just figure out the time for off-chain to react to deposit request, and submit approve 0 transaction shortly before this reaction time to ensure ingresso transaction executes after approve 0 transaction to make it revert.
Operator will waste gas on reverted transactions, user can disrupt protocol service and can also selectively censor transactions/actions if they're batched together in 1 transaction with user's deposit action, allowing user to do all kinds of malicious things.
```

## Recommendation
Consider depositing min(approved, requested) amount (and skipping deposit if approved == 0) when doing it via ingresso, which will avoid any reverts during deposits.

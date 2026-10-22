# [M] Excess eth is not refunded

## Summary
Severity: Medium
Contest weight: 0.4694
Dataset id: 16837
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability exists in the ArbitraryCallsProposal contract, which allows a caller to supply an amount of ether (msg.value) that is intended to fund a series of arbitrary external calls. The contract tracks the remaining ether in a local variable called ethAvailable, decreasing it by the value specified for each individual call. However, after all calls have been processed the contract does not include any logic to return the leftover ethAvailable to the original sender. As a result, when the total value of the specified calls is lower than the ether supplied by the user, the excess ether remains trapped inside the contract. This behavior arises from a missing refund step at the end of the _executeArbitraryCalls function, where the remaining balance should be transferred back to msg.sender but is omitted. An attacker or any user can exploit this condition simply by over‑paying for a proposal; the surplus ether will be retained by the contract indefinitely, effectively leaking value. The impact is that users who unintentionally or intentionally send more ether than required lose access to the unused portion, leading to a reduction in their effective balance and a potential erosion of trust in the protocol’s accounting guarantees. The issue manifests whenever a proposal includes calls whose combined value is less than the ether attached to the transaction, which can happen in normal usage if the caller miscalculates or deliberately over‑pays. All participants who interact with the proposal mechanism are affected, especially those who rely on precise ether budgeting for governance actions or financial operations. The flaw was uncovered during a Code4rena audit by inspecting the flow of ether inside the function and noticing the absence of a refund statement. It is subtle because the contract does not emit any warning or error for the leftover funds, making the leakage easy to miss during casual testing. The bug belongs to the class of "missing refund" or "value leakage" vulnerabilities, where a contract fails to return excess user-supplied assets after completing its intended logic. From a user’s perspective the symptoms include a transaction that appears successful while the sender’s wallet shows a lower-than‑expected balance, with no corresponding receipt of the unused ether. The expected behavior is that the user’s surplus ether would be returned, but in reality it stays locked in the contract. To remediate the issue, the contract should calculate the remaining ethAvailable after processing all arbitrary calls and explicitly transfer that amount back to the caller, thereby restoring the intended accounting invariants and preventing unintended fund loss.

## Proof of Concept
1. Observe the [_executeArbitraryCalls function](https://github.com/PartyDAO/party-contracts-c4/blob/main/contracts/proposals/ArbitraryCallsProposal.sol#L37)

```solidity
function _executeArbitraryCalls(
        IProposalExecutionEngine.ExecuteProposalParams memory params
    )
    internal
    returns (bytes memory nextProgressData)
{
...
uint256 ethAvailable = msg.value;
    for (uint256 i = 0; i < calls.length; ++i) {
        // Execute an arbitrary call.
        _executeSingleArbitraryCall(
            i,
            calls[i],
            params.preciousTokens,
            params.preciousTokenIds,
            isUnanimous,
            ethAvailable
        );
        // Update the amount of ETH available for the subsequent calls.
        ethAvailable -= calls[i].value;
        emit ArbitraryCallExecuted(params.proposalId, i, calls.length);
    }
....
}
```

2. As we can see user provided msg.value is deducted with each calls[i].value
3. Assume user provided 5 amount as msg.value and made a single call with calls[0].value as 4
4. This means after calls have been completed ethAvailable will become 5-4=1
5. Ideally this 1 eth should be refunded back to user but there is no provision for same and the fund will remain in contract

## Recommendation
At the end of `_executeArbitraryCalls` function, refund the remaining ethAvailable back to the user.

Will refund unused ETH at the end of executing arbitrary calls.

[0xble (PartyDAO) resolved](https://github.com/code-423n4/2022-09-party-findings/issues/186#issuecomment-1264679434):

Resolved: <https://github.com/PartyDAO/partybidV2/pull/135>

This is a form of leaking value - agree with Medium risk.

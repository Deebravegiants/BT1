# [H] Unauthorized pledge via open token approval

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23488
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Attacker can make pledge on behalf of users if those users have approved PledgeManager to spend their tokens

Description: PledgeManager requires users to approve it to spend their tokens in order to make pledges. Users can do this by either:
1) using IERC20Permit::permit which enforces a nonce for the signer, deadline and domain separator
2) manually by calling IERC20::approve
If users use the manual method 2) and leave an open token approval, an attacker can call PledgeManager::pledge to make a pledge on their behalf since this function never enforces that msg.sender == data.signer.
Impact: Attacker can make pledges on behalf of innocent users which spends those users' tokens. It is common for users to have max approvals for protocols they use often, even though they don't intend to spend all their tokens with that protocol.

## Recommendation
Recommended Mitigation: In PledgeManager::pledge, when not using IERC20Permit::permit enforce that msg.sender == data.signer:
```solidity
if (data.usePermit) {
    IERC20Permit(stablecoin).permit(
        signer,
        address(this),
        finalStablecoinAmount,
        block.timestamp + 300,
        data.permitV,
        data.permitR,
        data.permitS
    );
}
else if(msg.sender != signer) revert MsgSenderNotSigner();
```
Alternatively always use msg.sender similar to how PledgeManager::refundTokens works.

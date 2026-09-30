# [M] Auction won't work correctly with fee-on-transfer & rebasing tokens

## Summary
Severity: Medium
Contest weight: 0.1206
Dataset id: 14814
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The code in createAuction does the following:
IERC20(reserveToken).transferFrom(msg.sender, address(this), reserveAmount);
state.reserves = reserveAmount;
so it basically caches the expected transferred amount. This will not work if the reserveToken has a fee-on-transfer mechanism, since the actual received amount will be less because of the fee. It is also a problem if the token used had a rebasing mechanism, as this can mean that the contract will hold less balance than what it cached in state.reserves for the auction, or it will hold more, which will be stuck in the protocol.

## Recommendation
You can either explicitly document that you do not support tokens with a fee-on-transfer or rebasing mechanism or you can do the following:
1. For fee-on-transfer tokens, check the balance before and after the transfer and use the difference as the actual amount received.
2. For rebasing tokens, when they go down in value, you should have a method to update the cached reserves accordingly, based on the balance held. This is a complex solution.
3. For rebasing tokens, when they go up in value, you should add a method to actually transfer the excess tokens out of the protocol.

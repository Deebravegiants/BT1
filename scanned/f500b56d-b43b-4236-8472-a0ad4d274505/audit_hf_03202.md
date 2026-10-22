# [M] Solmate safetransfer and safetransferfrom

## Summary
Severity: Medium
Contest weight: 0.2069
Dataset id: 17783
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The safetransfer and safetransferfrom don't check the existence of code at the token address. This is a known issue while using solmate's libraries. Hence this may lead to miscalculation of funds and may lead to loss of funds, because if safetransfer() and safetransferfrom() are called on a token address that doesn't have a contract in it, it will always return success, bypassing the return value check. Due to this protocol will think that funds have been transferred successfully, and records will be accordingly calculated, but in reality, funds were never transferred. So this will lead to miscalculation and possibly loss of funds. llback.sol#L143 'token_.safeTransfer(to_, amount_);' llback.sol#L152 'token_.safeTransferFrom(msg.sender, address(this), amount_);' ller.sol#L108 'token.safeTransfer(to_, send);' ller.sol#L187 'quoteToken.safeTransferFrom(msg.sender, address(this), amount_);' ller.sol#L195 'quoteToken.safeTransfer(callbackAddr, amountLessFee);' ller.sol#L210 'payoutToken.safeTransferFrom(owner, address(this), payout_);' ller.sol#L214 'quoteToken.safeTransfer(owner, amountLessFee);' ller.sol#L89 'underlying_.safeTransfer(recipient_, payout_);' ller.sol#L114 'underlying_.safeTransferFrom(msg.sender, address(this), amount_);' ller.sol#L152 'underlying.safeTransfer(msg.sender, amount_);' er.sol#L90 'payoutToken_.safeTransfer(recipient_, payout_);' er.sol#L114 'underlying_.safeTransferFrom(msg.sender, address(this), amount_);' er.sol#L151 'meta.underlying.safeTransfer(msg.sender, amount_);' k.sol#L42 'payoutToken_.safeTransfer(msg.sender, outputAmount_);'

## Recommendation
Use openzeppelin's safeERC20 or implement a code existence check.

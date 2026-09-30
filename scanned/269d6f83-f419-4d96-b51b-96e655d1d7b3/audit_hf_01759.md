# [M] Replace createRetryableTicketNoRefundAliasRewrite() with depositEth()

## Summary
Severity: Medium
Contest weight: 0.0541
Dataset id: 9655
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function _startBridge() of the ArbitrumBridgeFacet uses createRetryableTicketNoRefundAliasRewrite(). According to the docs: address-aliasing, this method skips some address rewrite magic that depositEth() does.
Normally depositEth() should be used, according to the docs depositing-and-withdrawing-ether.

## Recommendation
Replace createRetryableTicketNoRefundAliasRewrite() with depositEth().

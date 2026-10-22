# [M] Creator fees may be burned

## Summary
Severity: Medium
Contest weight: 0.1133
Dataset id: 16334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`royaltyInfo`, `getRoyalties`, or `getFeeRecipients` may return `address(0)` as the recipient address. While the value 0 is correctly handled for the royalties itself, it is not for the address. In such a case, the ETH amount will be sent to `address(0)`, i.e. it is burned and lost.

## Recommendation
In your logic for determining the recipients, treat `address(0)` as if no recipient was returned such that the other priorities / methods take over.

We are looking into options here to improve.

We believe this is Medium risk, burning a percent of the sale revenue is a form of leaking value. Otherwise the sale works as expected and the collector does get the NFT they purchased.

The royalty APIs we use are meant to specific which addresses should receive payments and how much they each should receive. As the warden noted, we try to ignore entries which specify a 0 amount… but did not filter out address(0) recipients with >0 requested. Originally we were thinking this was a way of requesting that a portion of the sale be burned since that seems to be what the data is proposing.

However we agree that this is more likely a configuration error. Since our market uses ETH and not ERC20 tokens, it’s unlikely that creators would actually want a portion of the proceeds burned. We are exploring a change to send the additional revenue to the seller instead of burning the funds in this scenario.

Case of protocol leaked value: Medium severity is appropriate.

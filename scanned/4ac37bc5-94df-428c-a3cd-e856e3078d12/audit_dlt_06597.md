# [?] [Internally found]  Underflow in voucherRequestId preventing the penalization

## Summary
Severity: Unknown
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-09-01
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/138
Type: hats-finding

## Details
This is an issue which was found internally, I'm putting it there so no one can claim it:

> We're trying to obtain requestId by subtracting 1 from the overall count. The thing is that if the profile doesn't have any active requests at the moment then this counter will be nullified, like [here](https://github.com/Proof-Of-Humanity/proof-of-humanity-v2-contracts/blob/bab5585ae19164460342bd9f3e0192d4ee565bf6/contracts/ProofOfHumanity.sol#L1177) for instance. and thus thins condition will always underflow for such profiles which isn't really that rare occurence.


The lies in that we subtract 1 
(`uint256 voucherRequestId = voucherHumanity.requestCount[voucherHumanity.owner] - 1;`) before checking if there is a request (if (`voucherRequestId != 0)`). So if there is no request, we'll have an underflow.


The fix is to check that the request count is non null before substracting.

# [H] DoS at process vouch fundion leads to loss of funds

## Summary
Severity: High
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-08-30
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/114
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x38dd53b2121a7550200ba310d0946759407033e593b9b79d11975aed98b3c30c
**Severity:** high

**Description:**
**Description**\
process vouch fundion can be DoSed leading to DoS of executeRequest 

**Attack Scenario**\
If a penalty should be applied to a vouche in processVouches function it leads to DoS of the function as we see it substracts 1 from `voucherHumanity.requestCount[voucherHumanity.owner]`so if requestCount for underlying user is zero it would revert 
```solidity 
           if (applyPenalty) {
                // Situation when vouching address is in the middle of renewal process.
                uint256 voucherRequestId = voucherHumanity.requestCount[voucherHumanity.owner] - 1;
                if (voucherRequestId != 0) voucherHumanity.requests[voucherRequestId].punishedVouch = true;

                delete voucherHumanity.owner;

                emit HumanityDischargedDirectly(request.vouches[lastProcessed]);
            }
```
when a user execute a request, requestCount of requester would be deleted so it has zero value after user has claimed its humanity 
```solidity 
        delete humanity.requestCount[request.requester];
```
this prevents processVouches to be executed after an index that has applyPenalty leading to loss of funds as it prevents executeRequest to be performed

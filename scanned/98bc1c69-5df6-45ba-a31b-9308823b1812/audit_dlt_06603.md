# [H] Malicious user can DoS claim humanity at vouching state

## Summary
Severity: High
Chain: Smart contract
Component: Proof-Of-Humanity-V2
Published: 2024-08-29
Source: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/99
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x9b5ca14e13e3ca7cb1c1604dfcf6da3a45396b7a53187095ea58e0dc035cb562
**Severity:** high

**Description:**
**Description**\
Malicious user can DoS claim humanity at vouching state 

**Attack Scenario**\
`fundRequest` enables users to fund a request during vouching state, however if a request is fully funded a user can call this function with zero msg.value then _contribute would set `round.sideFunded = Party.None` whcih DoS the advance state function because of the following check: 
```solidity
require(request.challenges[0].rounds[0].sideFunded == Party.Requester);
```
 Scenario : 
1- a request is fully funded its 0 round `round.sideFunded = Party.Requester`
2- Malicious user calls the `fundRequest` function with zero msg.vale 
```solidity
 function fundRequest(bytes20 _humanityId, uint256 _requestId) external payable {
        Request storage request = humanityData[_humanityId].requests[_requestId];
        require(request.status == Status.Vouching);

        ArbitratorData memory arbitratorData = arbitratorDataHistory[request.arbitratorDataId];
        uint256 totalCost = arbitratorData.arbitrator.arbitrationCost(arbitratorData.arbitratorExtraData).addCap(
            requestBaseDeposit
        );

        _contribute(_humanityId, _requestId, 0, 0, Party.Requester, totalCost);
    }
```

then the _contribute would be performed, contribution has 0 value and required amount also would be zero, and since `round.sideFunded == Party.Requester` so it updates round.sideFunded to Party.None which prevents user to `advanceState` and claim its humanity 
```solidity
        uint256 contribution = msg.value;
        uint256 requiredAmount = _totalRequired.subCap(
            _side == Party.Requester ? round.paidFees.forRequester : round.paidFees.forChallenger
        );
        if (requiredAmount <= msg.value) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Proof-Of-Humanity-V2-0xef0709445d394a22704850c772a28a863bb780b0/issues/99_

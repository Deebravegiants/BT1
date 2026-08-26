# [M] Bad source of randomness

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-holograph
Published: 2022-10-25
Source: https://github.com/code-423n4/2022-10-holograph-findings/issues/427
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-10-holograph/blob/f8c2eae866280a1acfdc8a8352401ed031be1373/contracts/HolographOperator.sol#L491-L511


# Vulnerability details

## Impact
Using block.number and block.timestamp as a source of randomness is commonly advised against, as the outcome can be manipulated by calling contracts. In this case a compromised layer-zero-endpoint would be able to retry the selection of the primary operator until the result is favorable to the malicious actor.

## Proof of Concept
An attack path for rerolling the result of bad randomness might look roughly like this:

```js
function attack(uint256 currentNonce, uint256 wantedPodIndex, uint256 numPods, uint256 wantedOperatorIndex, uint256 numOperators,  bytes calldata bridgeInRequestPayload) external{

    bytes32 jobHash = keccak256(bridgeInRequestPayload);

    //same calculation as in HolographOperator.crossChainMessage
    uint256 random = uint256(keccak256(abi.encodePacked(jobHash, currentNonce, block.number, block.timestamp)));

    require(wantedPodIndex == random % numPods)
    require(wantedOperatorIndex == random % numOperators);

    operator.crossChainMessage(bridgeInRequestPayload);
}
```

The attack basically consists of repeatedly calling the `attack` function with data that is known and output that is wished for until the results match and only then continuing to calling the operator.


## Tools Used

Manual Review

## Recommended Mitigation Steps
Consider using a decentralized oracle for the generation of random numbers, such as [Chainlinks VRF](https://docs.chain.link/docs/vrf/v2/introduction/).


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-10-holograph-findings/issues/427_

# [M] Allowing duplicated anchors could cause bias on anchor price.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-vader
Published: 2021-04-28
Source: https://github.com/code-423n4/2021-04-vader-findings/issues/314
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

In `Router.sol`, the setup of the five anchors can be interrupted by anyone adding a new anchor due to the lack of access control of the `listAnchor` function. Also, duplicate anchors are allowed. If the same anchor is added three times, then this anchor biases the result of `getAnchorPrice`.

## Proof of Concept

Referenced code:
[Router.sol#L245-L252](https://github.com/code-423n4/2021-04-vader/blob/main/vader-protocol/contracts/Router.sol#L245-L252)

PoC: [Link to PoC](https://drive.google.com/drive/folders/1W3jhlWIIh7FxTLZET3z49yA0DBvlbcPg?usp=sharing)
See the file `200_listAnchor.js` for a PoC of this attack. To run it, use `npx hardhat test 200_listAnchor.js`.

## Tools Used

None

## Recommended Mitigation Steps

Only allow `listAnchor` to be called from the deployer by adding a `require` statement. Also, check if an anchor is added before by `require(_isCurated == false)`.

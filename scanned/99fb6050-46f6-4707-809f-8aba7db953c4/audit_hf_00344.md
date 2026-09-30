# [H] Unable to call some functions in

## Summary
Severity: High
Contest weight: 0.2746
Dataset id: 1711
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BoostCore.sol will always be set as the owner of Boost provided incentive contracts because the initializer is called here within _makeIncentives. Therefore any function using the onlyOwner modifier within the incentive contracts must be called by BoostCore. For example, there is no way to call drawRaffle or clawback from the BoostCore contract. createBoost is called to create a new boost. Each incentive is initialized by the call to _makeIncentives. Within _makeIncentives the initializer is called for each incentive. The initializer function within each incentive contract sets the owner as msg.sender which would be the BoostCore contract.
Internal pre-conditions
1. Boost is created using the out of the box incentive contract as one of the incentives including: ERC20Incentive, CGDAIncentive, ERC20VariableIncentive, and ERC1155Incentive
External pre-conditions
Attack Path
1. User calls createBoost to create a new Boost
2. They choose to use an out of the box incentive contract listed above
3. They are initialized with BoostCore as the owner
• No winner can be drawn for raffle contests through ERC20Incentive contract
• Any funds in the contract that need to be rescued cannot be retrieved through clawback

## Recommendation
Owner should be specified in the init payload by the user similarly to how its done for the budget contracts here

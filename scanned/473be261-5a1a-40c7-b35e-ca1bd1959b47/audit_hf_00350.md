# [M] The incentive contracts are not

## Summary
Severity: Medium
Contest weight: 0.5948
Dataset id: 1717
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol wants to work with all kind of tokens including rebasing tokens. From weirdERC20 we can read more about Balance Modifications Outside of Transfers (rebasing/airdrops) section which states
Some tokens may make arbitrary balance modifications outside of transfers (e.g. Ampleforth style rebasing tokens, Compound style airdrops of governance tokens, mintable/burnable tokens).
Some smart contract systems cache token balances (e.g. Balancer, Uniswap-V2), and arbitrary modifications to underlying balances can mean that the contract is operating with outdated information.
One such example of not supporting in the code is the ERC20Incentive::clawback() function
```solidity
function clawback(bytes calldata data_) external override onlyOwner returns (bool) {
    ClawbackPayload memory claim_ = abi.decode(data_, (ClawbackPayload));
    (uint256 amount) = abi.decode(claim_.data, (uint256));
    if (strategy == Strategy.RAFFLE) {
        // Ensure the amount is the full reward and there are no raffle entries, then reset the limit
        if (amount != reward || claims > 0) revert BoostError.ClaimFailed(msg.sender, abi.encode(claim_));
        limit = 0;
    } else {
        // Ensure the amount is a multiple of the reward and reduce the max claims accordingly
        if (amount % reward != 0) revert BoostError.ClaimFailed(msg.sender, abi.encode(claim_));
        limit -= amount / reward;
    }
```
The variable reward is being used in these if conditions, reward is set during initialization of the contract. It is either set as the full amount for raffles or the amount of reward per person for pools.
In the initialize() function, suppose that the reward amount in the data is sent as 10e18, this is set as reward for the raffle after confirming by checking the balance of the contract.
Now suppose after some time the balance has changed due to rebasing. The reward variable is still 10e18 but the actual balance of the contract is different.
In the clawback() function, the owner wants to withdraw the full amount of the raffle. If they provide the rebased balance of the contract, the function will revert due to the following if condition
```solidity
if (amount != reward || claims > 0) revert BoostError.ClaimFailed(msg.sender, abi.encode(claim_));
```
If they provide 10e18 as amount which was the original amount and the current balance of the contract is lower then the following line will cause a revert
```solidity
asset.safeTransfer(claim_.target, amount);
```
This is only one instance of an issue, these issues are present in the Incentive contracts which use ERC20s.
Similarly ERC20Incentive::drawRaffle() will also not work if the actual balance of the contract has changed to a lower amount.
The balances are outdated and will cause hindrances for all parties involved. Denial of Service when the balances rebase.

## Recommendation
Track the balances after each transfer in/out to keep updated data in the contracts.
Disclaimers
project.
Usage of all smart contract software is at the respective users’ sole risk and is the users’ responsibility.

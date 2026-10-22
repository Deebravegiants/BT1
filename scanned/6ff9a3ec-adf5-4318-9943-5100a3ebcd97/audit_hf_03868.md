# [M] min withdraw of 5 VUSD is not enough to pre-

## Summary
Severity: Medium
Contest weight: 0.5957
Dataset id: 20135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A vulnerability exists where a malicious user spam the contract with numerous withdrawal requests (e.g., 5,000). This would mean that genuine users who wish to withdraw their funds may find themselves unable to do so in a timely manner because the processing of their withdrawals could be delayed significantly.
The issue stems from the fact that there is no restriction on the number of withdrawal requests a single address can make. A malicious actor could repeatedly call the withdraw or withdrawTo function, each time with a small amount (min 5 VUSD), to clog the queue with their withdrawal requests.
```solidity
//E Burn vusd from msg.sender and queue the withdrawal to "to" address
function _withdrawTo(address to, uint amount) internal {
    //E check min amount
    not enough to prevent grief
    //E burn this amount from msg.sender
    burn(amount); // burn vusd from msg.sender
    //E push
    withdrawals.push(Withdrawal(to, amount * 1e12));
}
```
Given the maxWithdrawalProcesses is set to 100, and the withdrawal processing function processWithdrawals doesn't have any parameter to process from a specific index in the queue, only the first 100 requests in the queue would be processed at a time.
```solidity
uint public maxWithdrawalProcesses = 100;
//E create array of future withdrawal that will be executed to return
function withdrawalQueue() external view returns(Withdrawal[] memory queue) {
    //E check if more than 100 requests in withdrawals array
    uint l = _min(withdrawals.length-start, maxWithdrawalProcesses);
    queue = new Withdrawal[](l);
    for (uint i = 0; i < l; i++) {
        queue[i] = withdrawals[start+i];
    }
}
```
In the case of an attack, the first 100 withdrawal requests could be those of the attacker, meaning that the genuine users' requests would be stuck in the queue until all of the attacker's requests have been processed. Moreover the fact that we can only withdraw up to 1 day long when our withdraw request is good to go.
This could result in significant delays for genuine users wanting to withdraw their funds, undermining the contract's usability and users' trust in the platform.

## Recommendation
Either limit number of withdrawal requests per address could be a first layer of defense even if it's not enough but I don't see the point why this limit is included so removing it could mitigate this. Otherwise you could implement a priority queue regarding amount to be withdrawn

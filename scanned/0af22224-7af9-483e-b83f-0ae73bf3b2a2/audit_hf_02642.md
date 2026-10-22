# [M] Many Inserts Can Take Place In One Block At Low Gas Fees

## Summary
Severity: Medium
Contest weight: 0.2466
Dataset id: 14286
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For both EIP-7002 and EIP-7251, it is possible to queue a very large number of new requests in a single block. The only validity checking in the contract is that the fee is paid and that the data is correctly formatted. It is therefore easy to submit a large number of requests without needing to operate a validator.
This circumvents the intended restriction of the fee mechanism because the fees only update between blocks. Within a single block, the fee will not change, regardless of the number of new submissions that the contract receives.
The impact of this form of attack is limited as the attacker would still need to pay large quantities of gas. In testing, a single request costs roughly 75k gas. Meaning that it is possible to submit around 400 new requests within a gas limit of 30 million.
However, an attacker can perform some optimisations to lower this gas cost. Roughly 88% of the gas cost of a request comes from 3 SSTORE instructions. These are used to store the input data from the user and the address of the user in storage. One way to lower the cost of these SSTORE operations is by not writing new data to the slot, but instead writing the value that is already in the slot. This is easy for the first two SSTORE operations, an attacker simply changes the input data to the data that is already in the slot. When doing so, the cost of a request drops to roughly 35k gas. The third SSTORE writes the address of the caller. In order to optimise this, the attacker would have to have their address already written to this slot. This can be done by repeating this attack multiple times, allowing for more requests each iteration as the attacker’s address is written to more slots each time and the average cost per request drops. With this technique the cost of a request is roughly 15k gas. Allowing a theoretic total of 2000 requests in a block.
Consider the following possible impacts of this form of attack:
1. Fee Avoidance – A large protocol with many validators would be wise to batch up their consolidation and withdrawal requests in this manner to give all their users the benefits of the lowest available fees. This could lead to many entries being submitted at lower than intended fees.
2. Storage Bloat – The development team stated that a strong motivation for the fees was to limit the use of storage space on the execution layer. If the beneficial pattern for users is to submit very large numbers of requests in a single block, then this would lead to heavier, not lighter, usage of the contract’s storage space.
3. Denial-of-Service And Unreasonable Fees – The potential effect of a large number of submissions in a single block is to inflate the fee and create a backlog of requests that have to be processed. For example, if an attacker sends 2000 EIP-7002 requests in a single block, it would take 25 minutes to process these requests, delaying all the subsequent requests in the meantime. Additionally, the fee would be inflated to higher than 1 ETH for 130 minutes. EIP-7251 requests are slightly more gas-intensive but are processed much slower. Given 1650 requests for EIP-7251 are made in a single block, there would be a delay of 330 minutes and an inflated fee > 1 ETH for 190 minutes. These types of attacks may also occur unintentionally on a smaller scale when a large protocol sends many requests in a single block.
4. Fee Griefing Consider a submission contract similar to those in the EIPs:
Pectra System Contracts Bytecode
uint256 fee = uint256(bytes32(feeData));
// Add the request.
bytes memory callData = abi.encodePacked(pubkey, amount);
(bool writeOK,) = WithdrawalsContract.call{value: fee}(callData);
If a submission to a contract such as this were to appear in the mempool, it could be frontrun by transactions in a previous block that pump the fee to potentially thousands of ETH, which this contract would then pay. Of course, a contract holding thousands of ETH should check the fee before sending, as should any contract, but it remains a potential attack vector.

## Recommendation
Consider limiting the number of submissions per block for these contracts.
Pectra System Contracts Bytecode

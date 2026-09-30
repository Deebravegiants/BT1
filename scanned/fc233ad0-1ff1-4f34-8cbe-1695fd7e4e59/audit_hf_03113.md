# [M] Usage of deprecated transfer() can result in

## Summary
Severity: Medium
Contest weight: 0.1202
Dataset id: 17577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function withdrawPayments() is used by the Owners to withdraw the fees. ever this limit your protocol to interact with others contracts that need more than that to process the transaction. Specifically, the withdrawal will inevitably fail when: 1. The withdrawer smart contract does not implement a payable fallback function. 2. The withdrawer smart contract implements a payable fallback function which uses more than 2300 gas units. 3. The withdrawer smart contract implements a payable fallback function which needs less than 2300 gas units but is called through a proxy that raises the call’s gas usage above 2300. net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/

## Recommendation
Use call instead of transfer(). Example: (bool succeeded, ) = _to.call{value: _amount}(""); require(succeeded, "Transfer failed."); Fair considering recipient may be a contract with custom logic for receive(). But this is definitely recoverable if the fee recipient wasn't able to receive funds. Moved to .call. Fix here. Confirmed fix.

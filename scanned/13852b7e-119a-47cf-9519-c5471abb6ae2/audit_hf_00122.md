# [M] instead of `call`

## Summary
Severity: Medium
Contest weight: 0.1053
Dataset id: 300
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
function withdraw(uint amount) external {
    require(amount <= ethBalance[msg.sender]);
    ethBalance[msg.sender] = ethBalance[msg.sender].sub(amount);
    msg.sender.transfer(amount);
    emit Withdraw(msg.sender, amount);
}

To withdraw ETH, it uses `transfer()`, this transaction will fail inevitably when:

  1. The withdrawer smart contract does not implement a payable function.
  2. Withdrawer smart contract does implement a payable fallback which uses more than 2300 gas unit.
  3. The withdrawer smart contract implements a payable fallback function that needs less than 2300 gas units but is called through proxy, raising the call’s gas usage above 2300.

Recommend using `call()` to send ETH.

## Recommendation
No recommendation

# [M] Front Running claimMessage on L1 and L2

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
The front-runner on L1 or L2 can front run the `claimMessage` transaction, as long as the `fee` is greater than the gas cost of the claiming the message and `feeRecipient` is not set, consequently the fee will be transferred to the `message.sender`(the front runner) once the message is claimed. As a result, postman would lose the incentive to deliver(claim) the message on the destination layer.   

#### Examples


**contracts/contracts/messageService/l1/L1MessageService.sol:L137-L142**
```solidity
if (_fee > 0) {
  address feeReceiver = _feeRecipient == address(0) ? msg.sender : _feeRecipient;
  (bool feePaymentSuccess, ) = feeReceiver.call{ value: _fee }("");
  if (!feePaymentSuccess) {
    revert FeePaymentFailed(feeReceiver);
  }
```


**contracts/contracts/messageService/l2/L2MessageService.sol:L162-L168**
```solidity
if (_fee > 0) {
  address feeReceiver = _feeRecipient == address(0) ? msg.sender : _feeRecipient;
  (bool feePaymentSuccess, ) = feeReceiver.call{ value: _fee }("");
  if (!feePaymentSuccess) {
    revert FeePaymentFailed(feeReceiver);
  }
}
```

#### Recommendation
There are a few protections against front running including flashbots service. Another option to mitigate front running is to avoid using msg.sender and have user use the signed `claimMessage` transaction by the Postman to claim the message on the destination layer

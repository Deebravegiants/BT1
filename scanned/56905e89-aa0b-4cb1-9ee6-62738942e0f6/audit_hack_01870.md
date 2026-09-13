# [M] Updating Message Service Does Not Emit Event

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
The function `setMessageService` allows the owner to update the message service address. However, it does not emit any event reflecting the change. As a result, in case the owner gets compromised, it can silently add a malicious message service, exploiting users' funds. Since, there was no event emitted, off-chain monitoring tools wouldn't be able to trigger alarms and users would continue using rogue message service until and unless tracked manually.

#### Examples


**contracts/TokenBridge.sol:L237-L240**
```solidity
function setMessageService(address _messageService) public onlyOwner {
  messageService = IMessageService(_messageService);
}

```

#### Recommendation

Consider emitting an event reflecting the update from the old message service to the new one.

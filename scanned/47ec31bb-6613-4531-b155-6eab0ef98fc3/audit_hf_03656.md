# [M] Migration can be bricked by sending a mes-

## Summary
Severity: Medium
Contest weight: 0.2680
Dataset id: 19737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The migration process halts and returns an error if any of the withdrawal data breaks from the specified format. However, the data for this migration comes from every call that has been made to the LegacyMessagePasser (0x00) address, and it is possible to send a transaction that would violate the requirements. The result is that the migration process would be bricked and need to be rebuilt, with some difficult technical challenges that we'll outline below.
Withdrawal data is saved in l2geth whenever a call is made to the LegacyMessagePasser address:
if addr == dump.MessagePasserAddress {
    statedumper.WriteMessage(caller.Address(), input)
}
This will save all the calls that came via the L2CrossDomainMessenger. The expected format for the data is encoded in the L2CrossDomainMessenger. It encodes the calldata to be executed on the L1 side as:
abi.encodeWithSignature("relayMessage(...)", target, sender, message, nonce)
The migration process expects the calldata to follow this format, and expects the checks:
selector := crypto.Keccak256([]byte("relayMessage(address,address,bytes,uint256)"))[0:4]
if !bytes.Equal(data[0:4], selector) {
    return fmt.Errorf("invalid selector: 0x%x", data[0:4])
}
msgSender := data[len(data)-len(predeploys.L2CrossDomainMessengerAddr):]
if !bytes.Equal(msgSender, predeploys.L2CrossDomainMessengerAddr.Bytes()) {
    return errors.New("invalid msg.sender")
}
The migration process will be exited and the migration will fail if this assumption is violated.
However, since the function on the LegacyMessagePasser is public, it can also be called directly with arbitrary calldata:
function passMessageToL1(bytes memory _message) external {
    sentMessages[keccak256(abi.encodePacked(_message, msg.sender))] = true;
}
This allows us to submit calldata that would violate both of these checks and cause the migration to panic and fail.
While it may seem easy to filter these withdrawals out and rerun the migration, this solution would not work either. That's because, later in the process, we check that easy storage slot in the LegacyMessagePasser contract has a corresponding withdrawal in the migration:
for slot := range slotsAct {
    _, ok := slotsInp[slot]
    if !ok {
        return nil, fmt.Errorf("unknown storage slot in state: %s", slot)
    }
}
a new migration process to account for this issue, and remigrate with an untested system.
needing to run a less tested migration process (which could lead to further issues), and a significant amount of FUD in pausing a partially completed migration partway through. We think that the ability to unexpectedly shut down the migration causes enough structural damage as well as second-order financial damage to warrant high severity.

## Recommendation
Rather than throwing an error if withdrawal data doesn't meet the requirements, save a list of these withdrawals and continue. Include this list when prechecking withdrawals to ensure that they are included in the storage slot matching process, but not included in withdrawals to be transferred to the new system.
After coming up with this attack, we've noticed that someone has done exactly what we described and sent a message directly to the MessagePasser! Obviously this TX has nothing to do with us and we want to make sure Optimism is absolutely safe during migration. Furthermore, this TX should be traced and if a contestant is linked to this then they should clearly be disqualified from being rewarded.

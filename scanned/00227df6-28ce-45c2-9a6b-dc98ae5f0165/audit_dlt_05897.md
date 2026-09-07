# [?] Fix FAB-18528: remove panic in ifConfig func (#2828)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2021-08-11
Source: https://github.com/hyperledger/fabric/commit/497a177ffb818ed8f75578cb55a65ba2224a85ea
Type: security-commit

## Details
Fix FAB-18528: remove panic in ifConfig func (#2828)

Fix issues: FAB-18528. When received the constructed message from the malicious node (through the interface "chain.rpc.SendSubmit(dest uint64, request *orderer.SubmitRequest, report func(err error))"), all orderers will breakdown immediately.

Signed-off-by: sardChen <sard.chen@gmail.com>

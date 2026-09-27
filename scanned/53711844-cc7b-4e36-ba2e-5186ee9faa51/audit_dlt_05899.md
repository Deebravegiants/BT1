# [?] [FAB-18329] Fix data race in cluster/comm_test#TestRenewCertificates (#2089)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-11-09
Source: https://github.com/hyperledger/fabric/commit/901fe6ceccf0d85ed25cc62ad32a3fd65131800f
Type: security-commit

## Details
[FAB-18329] Fix data race in cluster/comm_test#TestRenewCertificates (#2089)

This commit fixes a data race in orderer/common/cluster/comm_test.go#TestRenewCertificates.

The race occurred because the TLS configuration was updated from the test goroutine,
while a gRPC connection was being established from another goroutine, and as a result,
the TLS configuration was loaded without memory synchronization with the first goroutine.

I made the test close the gRPC connections before reconfiguring the communication layer.

Change-Id: I82b9cc685e9160e480ce77ec7e0a233b106eb0e5
Signed-off-by: Yacov Manevich <yacovm@il.ibm.com>

Co-authored-by: yacovm <yacovm@li-3faaf6cc-2cd1-11b2-a85c-fd3f1da7bbdb.ibm.com>

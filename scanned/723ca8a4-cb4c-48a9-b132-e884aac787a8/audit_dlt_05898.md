# [?] [FAB-18333] Fix panic in cluster/comm#TestRenewCertificates

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-11-10
Source: https://github.com/hyperledger/fabric/commit/f1058a802cd6070ecb3e0aaf17793b8655940f70
Type: security-commit

## Details
[FAB-18333] Fix panic in cluster/comm#TestRenewCertificates

In the unit test TestRenewCertificates, node 2 is restarted and its certificates
are rotated.

It is tested that node 1 fails to re-connect to the old certificate until it is reconfigued.
However, since it is not aware of the new reconfiguration, the old gRPC stream might be stale
and it might not be detected, and the expected error that is checked results in a nil pointer panic.

This PR aims to fix the nil pointer panic, by repeatedly trying to use the stream until an error is returned.
This ensures that the gRPC stream is un-usable and when the server starts with a new certificate
it will still be un-usable.

Change-Id: I038624907ebab198bb3a193b137a47b2e7c970d0
Signed-off-by: Yacov Manevich <yacovm@il.ibm.com>

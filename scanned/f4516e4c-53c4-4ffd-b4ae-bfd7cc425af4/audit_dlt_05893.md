# [?] Fixed an error in building the plan for the endorsement. Periodically, the `endorse retry - org3 fail & 1 org2 peer fail - requires 2 from org1` test 

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2026-04-23
Source: https://github.com/hyperledger/fabric/commit/2190a1c8e0677cceed8a6ccc1604d793095fc481
Type: security-commit

## Details
Fixed an error in building the plan for the endorsement. Periodically, the `endorse retry - org3 fail & 1 org2 peer fail - requires 2 from org1` test fails with an error. I figured it out and added the TestMultiLayoutFailures1 test, which crashes in the old version of the code. (#5456)

Signed-off-by: Fedor Partanskiy <fredprtnsk@gmail.com>

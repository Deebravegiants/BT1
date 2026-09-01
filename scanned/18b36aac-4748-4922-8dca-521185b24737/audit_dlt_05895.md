# [?] Disable vulnerability scans for v2.2 and v2.4 (#4716)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2024-03-04
Source: https://github.com/hyperledger/fabric/commit/0ee5160526dddb1fc86ec90e829b78c265ff93a2
Type: security-commit

## Details
Disable vulnerability scans for v2.2 and v2.4 (#4716)

Fabric has recently ended maintenance of v2.2 and will
no longer backport dependency updates to v2.2 or v2.4.
All users are encouraged to use v2.5 at this point,
therefore just run the vulnerability scan for v2.5 and main branches.

Signed-off-by: David Enyeart <enyeart@us.ibm.com>

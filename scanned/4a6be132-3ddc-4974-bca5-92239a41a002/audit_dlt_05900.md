# [?] Fix data race in gossip/discovery test

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-09-10
Source: https://github.com/hyperledger/fabric/commit/65d0b62479ad80da77a5e01ae8c152751b38f0ce
Type: security-commit

## Details
Fix data race in gossip/discovery test

This change set fixes two data races:

1) A logger reference was overriden while the logger might be in use.
   I changed the implementation so that the logger will be injected.

2) A shared number was incremented by logger hooks that are instantiated
   multiple times for different peers.
   I made it so that each logger hook receives its own counter, which is
   no longer a counter but a map of log entries that are searched.

Change-Id: Ic69f604f30a16e1a1fb9050ba9145dfa38e05146
Signed-off-by: yacovm <yacovm@il.ibm.com>

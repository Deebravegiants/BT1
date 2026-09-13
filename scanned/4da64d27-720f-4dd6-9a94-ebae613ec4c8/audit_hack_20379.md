# [H] 5.2.6 ETH yield token bridge transactions use fixed gas and are not replayable

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** L1BlastBridge.sol#L219-L

**Description:** When using theL1BlastBridgeto bridge an ETH yield token, theOptimismPortalis called directly
instead of routing through theL1CrossDomainMessenger, and a fixed gas amount ofRECEIVE_DEFAULT_GAS_LIMIT
= 100_000gas is always used:

```
portal.depositTransaction(
Predeploys.L2_BLAST_BRIDGE,
_amount,
RECEIVE_DEFAULT_GAS_LIMIT,
false,
abi.encodeWithSelector(/* ... */)
);
```
As noCrossDomainMessengerintermediate contract is used, thefinalizeBridgeETHDirectbridge transactions
are not replayable. They will be executed once and if the transaction fails, the bridged ETH is lost (remains in the
aliasedL1BlastBridgeaddress on L2). This call might fail if thetoaddress consumes more than the allocated
RECEIVE_DEFAULT_GAS_LIMITgas in itsreceivefunction. The_minGasLimitparameter of thebridgeERC20*
functions is currently ignored for ETH yield tokens which can be very misleading for users and lead to losses.

**Recommendation:** Consider using the_minGasLimitparameter in_initiateBridgeERC20not only for the USD
yield tokens but also for the ETH yield tokens instead of the hardcodedRECEIVE_DEFAULT_GAS_LIMITgas limit.


# DRAFT

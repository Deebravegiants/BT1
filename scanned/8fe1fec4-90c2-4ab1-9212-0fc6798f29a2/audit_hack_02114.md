# [M] 6.3 Inconsistent DepositEvent Amount Units

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The ERC20Gateway.deposit function users provide the amount of tokens to extend as a
BaseInputParams.paramTwo in wei. This param in wei will contribute to the deposit leaf hash. Same
paramTwo in wei will be emitted in DepositEvent. On the destination domain recipient will need to
specify the same paramTwo in _depositMetadata.baseDepositInfo.paramTwo.

However, this is not consistent with savETHGateway. In savETHGateway.deposit the user provides
the KNOT that he wants to migrate. The savETHRegistry.knotDETHBalanceInIndex in gwei of this
KNOT will contribute to the deposit leaf hash. But the knotDETHBalanceInIndex in wei will be emitted
in Deposit tx. On push, _depositMetadata.amount in gwei will be converted to wei and the savETH
on the destination domain will be minted. In summary, inconsistency is that units of event do not match
the value from _depositMetadata.amount and the deposit leaf hash. Assuming that the endorsers
will be querying the depositMetadata for the attestation, an extra conversion of deposit event values will
be needed for one of these cases to compute the hash of the RPBS info.

Code corrected:

Blockswap has successfully resolved this inconsistency in various parts of the codebase (both
dispensers and ingestors).

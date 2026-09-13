# [M] 6.6 Gas Heavy Operation on Foreign Chain

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

ForeignChainTokenBridgeAdminProxy is supposed to be deployed on the Ethereum mainnet, thus
its gas consumption is critical. The current complexity of the updateTokenbridgeValidators is
actually O(m*n), where m is length of old list and n is length of new list. Complexity can be reduced to
O(m+n) if all old values in list were replaced by new list values. Also, the number of calls to other
contracts should be minimized. Currently, a lot of calls to bridgeValidators contract are done.

Specification corrected:

Q Blockchain wants to use IBridgeValidators interface implementation as it is without any
modifications, since it allows them easier integration with existing tokenbridge code. With this
requirement, current solution is sufficient. In addition, the O(m*n) complexity loop is done to lower the
number of calls between ForeignChainTokenBridgeAdminProxy and IBridgeValidators
contracts. According to Q Blockchain tests, this lowers the overall gas consumption.

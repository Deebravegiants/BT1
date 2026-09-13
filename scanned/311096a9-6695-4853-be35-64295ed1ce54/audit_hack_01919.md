# [M] 6.1 Public Setter Functions Can Be Frontrun

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

The following functions can only be executed once and have no access controls:

```
1.FxBaseRootTunnel.setFxChildTunnel
2.FxBaseChildTunnel.setFxRootTunnel
3.FxRoot.setFxChild
4.FxChild.setFxRoot
```
```
5.FxERC20.initialize
6.FxERC721.initialize
7.FxERC1155.initialize
```
If deployment and initialization is not done within one transaction it would be possible for a malicious
actor to frontrun the deployer's call to the functions and instead call them with malicious values first. This
will cause the deployer's function call to revert.

FxBaseRootTunnel and FxBaseChildTunnel are to be inherited by contracts in order to use the
bridging functionality of the Fx Portal. This may lead to problems with their deployment. Implementors
should be aware of this behavior, mitigate this and ensure/verify that initialization is done correctly. If their
setTunnel functions are frontrun, the contract will need to be redeployed. This can be expensive in terms
of gas.

The Wrapper contracts FxRoot and FxChild for the interaction with the StateSender have already
been deployed and initialized correctly. If a new instance of one of these contracts is deployed, the
deployer must verify that the functions are called correctly. For the Token contracts
FxERC20/ERC721/ERC115 used in the examples minimal proxy contracts are deployed the
initialize() function is called from contracts within the same transactions.


Risk accepted:

Polygon states:

```
It is a known risk that initialization functions can be frontrun, but this
is low-risk since there is no incentive for a malicious actor to do so.
```

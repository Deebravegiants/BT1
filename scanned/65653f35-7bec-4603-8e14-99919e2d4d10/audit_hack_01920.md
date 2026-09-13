# [M] 6.2 Use (Up to Date) Dependencies

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Partially Corrected

Several contracts present in lib or tokens are copy & pasted from third party repositories. An
exception to this pattern is the SafeERC20 library which is imported from a dependency listed in the
package.json file. This pattern is generally preferable. Note that several of the copy & pasted
dependencies are also from this OpenZeppelin contracts dependency, hence could simply be imported
from there.

Package.json lists the dependencies and the requirements on the version, while
package-lock.json allows to fix specific version.

This allows to effortlessly update to newer versions of these contract which may include bug fixes. Note
that this must be done with due care as functionality could change. Once a new version has been
deemed suitably safe, the new version can be fixed in package-lock.json.

Most copy & pasted contracts are old versions, furthermore the version of the OpenZeppelin dependency
is outdated. Notably, the implementation of ERC721 contains several changes reloading state after
beforeTokenTransfer(), which may have updated this data.

Code partially corrected:

The dependencies in package.json were changed to more recent versions. ERC20.sol and
IERC20.sol were updated to OpenZeppelin v4.7.3.

The other copy & pasted contracts in lib have not been updated.



Here, we list findings that have been resolved during the course of the engagement. Their categories are
explained in the Findings section.

Below we provide a numerical overview of the identified findings, split up by their severity.

```
Critical-Severity Findings 0
```
```
High-Severity Findings 1
```
- mapToken() Callable Only by Mappers Specification Changed

```
Medium-Severity Findings 2
```
- Description of toBoolean() Is Incorrect Specification Changed
- FxMintableERC20RootTunnel connectedToken Initialized Incorrectly Code Corrected

```
Low-Severity Findings 8
```
- Codehash Variable Type Could Be Set to Immutable Code Corrected
- FxMintableERC20ChildTunnel Has No withdrawTo Function Code Corrected
- FxMintableERC20RootTunnel Events Missing Code Corrected
- Outdated Compiler Version Code Corrected
- Return Value of _checkBlockMembershipInCheckpoint() Code Corrected
- SafeMath Library Is Redundant Code Corrected
- Unused Variable in FxMintableERC20RootTunnel Code Corrected
- _processMessageFromChild Comment Incorrect Specification Changed

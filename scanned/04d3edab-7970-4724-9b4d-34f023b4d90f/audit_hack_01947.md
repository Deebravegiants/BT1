# [H] 6.2 OperationsRegistry: No Access Control

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected


The purpose of the OperationsRegistry contract is to specify the set of actions identified by a
string name. As this contract lacks access control, anyone could modify the mapping between
operation and actions. This can be done through the addOperation function, which allows not only
adding a new operation but also modifying any existing one.

As a consequence, an attacker could modify the entries for existing operations. This could prevent the
corresponding verifications from succeeding, and thus compromise the availability of the system. An
attacker may as well delete the actions stored for an operation resulting in no verification on the calls
being done in OperationExecutor.aggregate().

The extensive documentation lacks a description of the OperationRegistry.

Code corrected:

Access control has been added: There is now an owner, only this owner can add/update operations to
the OperationRegistry.

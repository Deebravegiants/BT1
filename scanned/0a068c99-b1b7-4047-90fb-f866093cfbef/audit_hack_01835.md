# [M] Outdated documentation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
There are many changes within the system from the initial version that are not reflected in the documentation.

It is necessary to have updated documentation for the time of the audit, as the specification dictates the correct behaviour of the code base. 

#### Examples

Entities such as `iExecClerk` are the main point of entry in the documentation, however they have been replaced by proxy implementation in the code base (V5).

#### Recommendation
Up date documentation to reflect the recent changes and design in the code base.

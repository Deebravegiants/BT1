# [H] 6.3 Owner Not Initialized

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

Some contracts inherit Ownable and Initializable, but do not assign the owner in the initialize
function. If such contracts are deployed as a proxy, the owner field will be uninitialized (stays address 0)
and owner functionality would be unusable.


- GSNPaymaster inherits Initializable and BasePaymaster. BasePaymaster inherits Ownable.
    Function initialize of the GSNPaymaster only assigns value to stc field. The relayHub field
    can only be set by owner.
- ForeignChainTokenBridgeAdminProxy does not set owner in initialize.
- TokenBridgeAdminProxy is Initializable and Ownable. Owner is not initialized. Also, the Ownable
    functionality is not used anywhere.
- ExpertsMembership does not initialize owner. Also, the Ownable functionality is not used anywhere.

Code corrected:

Q Blockchain has done following fixes for the issues:

- Function initialize was removed from GSNPaymaster. The logic from it was moved to the
    constructor.
- Now the contract extends OwnableUpgradeable contract of openzeppelin library. The initialize
    functions calls _Ownable_init, that sets the owner.
- Now the contract extends OwnableUpgradeable contract of openzeppelin library. The initialize
    functions calls _Ownable_init, that sets the owner.
- Now the contract extends OwnableUpgradeable contract of openzeppelin library. The initialize
    functions calls _Ownable_init, that sets the owner.

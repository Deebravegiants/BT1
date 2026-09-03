# [H] auth collision possible

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-05-29
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/5
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
The auth mechanism of AccessControl.sol uses function selectors (msg.sig) as a (unique) role definition.
Also the _moduleCall allows the code to be extended.
Suppose an attacker wants to add the innocent looking function "left_branch_block(uint32)" in an new module.
Suppose this module is added via _moduleCall  and the attacker gets authorization for the innocent function.
This functions happens to have a signature of 0x00000000, which is equal to the root authorization.
This way the attacker could get authorization for the entire project.

Note: it's pretty straightforward to generate function names for any signature value, you can just brute force it because it's only 4 bytes.

## Proof of Concept
// https://github.com/code-423n4/2021-05-yield/blob/main/contracts/utils/access/AccessControl.sol#L90
    modifier auth() {
        require (_hasRole(msg.sig, msg.sender), "Access denied");
        _;
    }

// https://github.com/code-423n4/2021-05-yield/blob/main/contracts/Ladle.sol#L588
    function _moduleCall(address module, bytes memory moduleCall)
        private
        returns (bool success, bytes memory result)
    {
        require (modules[module], "Unregistered module");
        (success, result) = module.delegatecall(moduleCall);
        if (!success) revert(RevertMsgExtractor.getRevertMsg(result));
    }
}

// https://www.4byte.directory/signatures/?bytes4_signature=0x00000000
Text Signature	                        Bytes Signature
left_branch_block(uint32)	0x00000000

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-yield-findings/issues/5_

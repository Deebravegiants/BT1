# [H] Malicious `uriSetter` can harm the protocol

## Summary
Severity: High
Reporter: tsvetanovv
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L65-L69
Type: audit-issue

## Details
# Malicious `uriSetter` can harm the protocol

## Summary

Malicious `uriSetter` can harm the protocol

## Vulnerability Detail

In `MeritNFT.sol` we have `setBaseURI()` function:
```solidity
    /// @notice Sets the base token URI. Can only be called by an address with the default admin role
    /// @param _newBaseURI New baseURI
    function setBaseURI(string memory _newBaseURI) external onlyUriSetter {
        baseTokenURI_ = _newBaseURI;
    }
```

This function allows an address with the URI setter role to update the base URI of the tokens in the contract.

But as we see from the Readme:

> Is the admin/owner of the protocol/contracts TRUSTED or RESTRICTED?
>- Restricted

The function `setBaseURI` changes the base URI stored in the contract. This allows for changing the location where the metadata files are stored. A malicious URI setter could potentially change the base URI to a different location under their control. To prevent this we can add a two-step role access system for an extra layer of security. 
This will require at least two different roles to confirm the change before it can be implemented and will prevent a malicious admin from harming the protocol.

## Impact

A malicious URI setter could potentially change the base URI to a different location under their control. This would have catastrophic consequences for Beam.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L65-L69

## Tool used

Manual Review

## Recommendation

Add a two-step role access system for an extra layer of security. This will require at least two different roles to confirm the change before it can be implemented.

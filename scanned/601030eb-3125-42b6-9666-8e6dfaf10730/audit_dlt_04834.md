# [M] User can use the same signature to deploy and call on different chain

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/127
Type: sherlock-finding

## Details
minhquanym

high

# User can use the same signature to deploy and call on different chain

## Summary
https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/Factory.sol#L537-L547

Lacking a `chainId` in encoded data allow user to use same signature on different chain.

## Vulnerability Detail
A set of functions `deploy(...)` and `call(...)` required a signature of the call payload by a `SIGNER_ROLE` wallet to be used. User has to send the data with a signature to the contract to be validated. It will check that this signature is matched with the data then allowing user to deploy a new NFT or do a call. 

Since it does not encoded with `chainId` field, the same data payload and signature can be used in every chain that the project support. 

## Impact
User can use the same signature signed by `SIGNER_ROLE` on different chain without permission

## Code Snippet

The data payload is lacking `chainId` field.
```solidity
function deploy(
    string calldata templateName,
    uint256 templateVersion,
    bytes calldata initdata,
    bytes calldata signature
)
    external
    payable
    signedOnly(
        abi.encodePacked(
            msg.sender,
            templateName,
            templateVersion,
            initdata
        ),
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/127_

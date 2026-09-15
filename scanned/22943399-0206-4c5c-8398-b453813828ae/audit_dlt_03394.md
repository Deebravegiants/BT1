# [M] Insecure randomness  in getPseudoRand(uint256 modulus){}  function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-11
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/60
Type: code-finding

## Details
# Handle

JMukesh


# Vulnerability details

## Impact
insecure randomness due to a modulo on block.timestamp, now or blockhash. These can be influenced by miners to some extent so they should be avoided

## Proof of Concept

  https://github.com/code-423n4/2021-05-nftx/blob/main/nftx-protocol-v2/contracts/solidity/NFTXVaultUpgradeable.sol#L418

## Tools Used
 slither

## Recommended Mitigation Steps
use chainlink vrf

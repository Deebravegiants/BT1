# [H] The patch is not sufficient: there is another insidious exploit that can cause the same critical consequences

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-ens-mitigation
Published: 2022-12-20
Source: https://github.com/code-423n4/2022-12-ens-mitigation-findings/issues/12
Type: code-finding

## Details
# Lines of code

https://github.com/ensdomains/ens-contracts/blob/69af5ea4fa1bb21a3ef240dd219b574d0e207421/contracts/wrapper/NameWrapper.sol#L137-L140


# Vulnerability details

## Status

+ Has been reported to and confirmed by Jeff (ENS team)

## Note to the Judge

I am not sure whether I should label this as a _newly-identified High_ or a _mitigation hard error_. The root cause of this issue seems as same as the original report, but this requires us to write a more sophisticated (and creative) exploit. (maybe mitigation hard error?)

## Description 

The basic root cause of [__H-02__](https://github.com/code-423n4/2022-11-ens-findings/issues/16) is implied unwrapping, where the hacker can re-register an ETH2LD node (to himself) via the old  .eth registrar controller after the ETH2LD's expiration. As a result, the hacker can implicitly unwrap any sub-domains regardless of their burnt fuses. 

The following check was added to validate whether an ETH2LD is wrapped or not.

```solidity=
            if (
                registrarExpiry > block.timestamp &&
                registrar.ownerOf(uint256(labelHash)) != address(this)
            ) {
                owner = address(0);
            }
```

For the attack strategy we provided in the original report (which is most intuitive), the patch is sufficient. 

However, after checking the mitigation deeper, I observe there is another insidious attack strategy that can bypass the current patch.

Note that the current patch only checks the the registrar owner (i.e., `registrar.ownerOr`) but not the registry owner (i.e., `ens.owenr`) for an ETH2LD.

As a result, if the hacker sets the registrar owner (i.e., `registrar.ownerOr`) as the NameWrapper contract but leave the registry owner (i.e., `ens.owner`) as the hacker himself, he is able to launch an implied unwrapping later.
 

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-12-ens-mitigation-findings/issues/12_

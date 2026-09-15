# [H] \[H08\] Endpoint registration can be frontrun

## Summary
Severity: High
Source: https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/ServiceProviderFactory.sol#L141
Type: audit-issue

## Details
An honest service provider’s call to the [ServiceProviderFactory.register function](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/ServiceProviderFactory.sol#L141) can be frontrun by a malicious actor in order to prevent any honest user from being able to register any endpoint.

The attacker can monitor the mempool for any calls to the `register` function, then frontrun them with their own call to the `register` function using the same `_endpoint` parameter.

This registers the endpoint under the attacker’s account so that the honest user’s attempt to register their endpoint will fail [on line 163](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/ServiceProviderFactory.sol#L163).

There is a cost to this attack. In particular, the attacker must stake the [minStake](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/ServiceTypeManager.sol#L26) or else [line 199](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/ServiceProviderFactory.sol#L199) will revert. This stake may be at risk of being slashed until the attacker has deregistered the endpoint and removed their stake. Since it takes at least ten blocks for an attacker to remove their stake after deregistering an endpoint, there is a window of opportunity for governance to slash the attacker. However, given the nature of the attack, it is not clear that it could be detected and punished within the ten blocks (about 2.5 minutes) lockup duration.

If `minStake` is small enough and/or the probability of getting detected and slashed is low enough, then this attack would have a low expected cost. Since these are currently unknowns, it is conservative to classify this issue as high severity.

To prevent a malicious service provider to register another service provider’s endpoint first, consider hashing the endpoint and the service provider’s address (`msg.sender`) together to create the endpoint’s `bytes32` identifier and then use it in a commit/reveal scheme during the registration process.

_**Update**: Fixed in [pull request # 573](https://github.com/AudiusProject/audius-protocol/pull/573/files), where the lockup period was changed from 10 blocks to 1 week. While the registration process may still be frontrun, there will be enough time for such behavior to be detected and punished via slashing._

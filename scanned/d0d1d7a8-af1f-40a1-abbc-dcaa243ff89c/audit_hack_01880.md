# [H] Agent Data Oracle Signed Credential Front-Running Attack

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

For almost every action as an `Agent`, the owner of the `Agent` is supposed to request `SignedCredential` data that contains all the relevant current info about the "off-chain" state of the `Agent`. New credentials can only be requested when the old one for this `Agent` is used or expired. Anyone can request these credentials, containing all the data about the call. So if the attacker consistently requests the credentials with the function and parameters that the actual `Agent` wouldn't want to call, the `Agent` won't be able to generate the credentials that are needed.

#### Recommendation

Ensure an `Agent` can always have new credentials that are needed. One solution would be to allow only an Agent's owner to request the credentials. The problem is that the beneficiary is also supposed to do that, but the beneficiary may also be a contract.

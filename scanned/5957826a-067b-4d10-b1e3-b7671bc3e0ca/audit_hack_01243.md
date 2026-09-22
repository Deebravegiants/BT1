# [C] Nomad incident: The Nomad Bridge, a cross-chain interoperability protocol, was attacked by hackers. This attack was due to the fact that the trust

## Summary
Severity: Critical
Target: Nomad
Loss: $ 154,000,000
Attack method: Contract Vulnerability
Published: 2022-08-02
Source: https://zerion.io/blog/nomad-bridge-hack/
Type: slowmist-incident

## Details
The Nomad Bridge, a cross-chain interoperability protocol, was attacked by hackers. This attack was due to the fact that the trusted root of the Nomad Bridge Replica contract was set to 0x0 during initialization, and the old root was not invalidated when the trusted root was modified. Constructing arbitrary messages to steal funds from the bridge, the attacker was able to extract over $190 million in value from the attack. So far, more than 40 addresses have returned over $36 million to Nomad.

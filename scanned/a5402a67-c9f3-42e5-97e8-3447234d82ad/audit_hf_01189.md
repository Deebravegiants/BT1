# [H] 3.2.1.1 Overly flexible configuration could allow TEE attestation bypass

## Summary
Severity: High
Contest weight: 0.3828
Dataset id: 5154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The batch poster's configuration system is too flexible, allowing modification of critical security parameters that could potentially enable malicious actors to bypass TEE attestation guarantees.
Most critically, empty values for LightClientAddress and HotShotUrl completely bypass Espresso validation while still allowing the TEE to produce valid attestation proofs.
Several critical configuration parameters can be modified to point to potentially malicious endpoints or alter security-critical behavior:
1. Network Endpoints:
• LightClientAddress: Can be configured to point to an invalid light client contract, potentially allowing verification of invalid HotShot consensus states.
• HotShotUrl: Can be set to any endpoint, potentially allowing the batch poster to receive manipulated consensus data.
• Critically, setting either of these to empty strings completely bypasses Espresso validation while still producing valid TEE attestations.
• ParentChainConfig.connection: Allows configuration of arbitrary L1 endpoints.
2. Security Parameters:
• UseEscapeHatch: Can be enabled to bypass HotShot consensus verification.
• EspressoSwitchDelayThreshold: Can be set to artificially low values to trigger escape hatch behavior.
The batch poster currently receives the same data that has been submitted by the transaction streamer and does not critically depend on the results from HotShot consensus. However, the flexibility in configuration could enable several attack vectors if it did:
1. Complete Validation Bypass: Empty values for LightClientAddress and HotShotUrl disable Espresso validation while maintaining valid TEE attestation.
2. Consensus Bypass: A malicious actor could configure endpoints to receive manipulated consensus data while still generating valid TEE attestations.
3. Verification Bypass: Invalid light client addresses could allow verification of incorrect consensus states.
4. Escape Hatch Abuse: Low threshold values could force the system to bypass consensus verification.
5. Chain Data Manipulation: Arbitrary L1 endpoints could provide manipulated chain data.
Impact: The impact could be severe if the batch poster's TEE attestation is used as a security guarantee while the configuration remains flexible. An attacker could potentially:
1. Generate valid TEE attestations for malicious batches.
2. Bypass consensus verification while maintaining apparent validity.
3. Manipulate the sequencing process through controlled endpoints.
Likelihood: The likelihood (as measured in the ease of exploitation) is medium to high for the batch poster if the TEE attestation is used as a standalone security guarantee, as the flexible configuration provides multiple vectors for potential exploitation.

## Recommendation
Add stricter configuration validation and ensure that critical endpoint parameters remain unchanged. The entry point script could be modified to receive a default configuration and to only allow a smaller subset of parameters to be modified.

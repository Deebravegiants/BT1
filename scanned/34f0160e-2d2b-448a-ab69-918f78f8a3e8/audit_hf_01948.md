# [M] Shadow factory does not work

## Summary
Severity: Medium
Contest weight: 0.0956
Dataset id: 10779
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
onlyOwner check in ShadowFactory is not initialized and thus has no owner. Solady's Ownable does not set the owner automatically on the deployment and requires calling _initializeOwner(), the way it is done in NFTShadow, for instance. As a result, any call of deployAndRegister() will always revert to checking the owner against msg.sender. So the deployment flow is not centalized (is not going through the single source) and owners will have to deploy Shadow instances manually, which can be vulnerable to initialize() frontrunning (if not called in the same transaction with the contract creation).

## Recommendation
Add the constructor in ShadowFactory and call _initializeOwner(msg.sender).

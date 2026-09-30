# [M] Non whitelisted user can also create agent

## Summary
Severity: Medium
Contest weight: 0.1237
Dataset id: 2663
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Non whitelisted user can also create agent by calling createAgentWithNFT instead of createAgentWithWhitelistUsers affecting the motive of protocol to only allow whitelisted user to create agent
createAgentWithWhitelistUsers function is designed by protocol with motive to only allow a particular amount of whitelisted users to create agent but this motive can be bypassed by anyone by calling createAgentWithNFT function instead.
Internal Pre-conditions
NA
External Pre-conditions
NA
Attack Path
1. Non whitelisted user can call createAgentWithNFT function instead of createAgentWithWhitelistUsers function and can create agent breaking the whitelist check
Non whitelisted user can also create agent breaking the motive of protocol to only allow whitelisted users to create agent.

## Recommendation
• Implement pausability feature in createAgentWithNFT function so that admin can pause the access of it until whitelist period for creation of agent and later can enable it.

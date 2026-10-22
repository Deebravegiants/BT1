# [M] Potential for cross-chain token replay attacks

## Summary
Severity: Medium
Contest weight: 0.3995
Dataset id: 6967
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the auth.ts middleware, JWT tokens are validated for a specific chain ID and service name:
```solidity
if (
    decoded.chainId !== chainId ||
    decoded.serviceName !== expectedServiceName
) {
    logger.warn(
        `Token validation failed for user ${decoded.sub}: Mismatched chainId or serviceName`
    );
    throw new Error("Authentication error: Mismatched chainId or serviceName");
}
```
While this validation is good, there are potential replay vulnerabilities if:
- The same JWT secret is shared across different chains or service deployments
- The application architecture changes to support multiple chains simultaneously
In a multi-chain environment, a token generated for one chain could potentially be replayed on another if proper isolation isn't maintained throughout the system.

## Recommendation
Ensure different JWT secrets are used for each chain and service. Include additional token validation specific to the target chain (e.g., chain-specific nonce). Implement token blacklisting after chain switching.

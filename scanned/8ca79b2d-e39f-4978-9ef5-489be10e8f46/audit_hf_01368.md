# [M] Overly restrictive API rate limiting

## Summary
Severity: Medium
Contest weight: 0.3798
Dataset id: 6966
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
15-minute window:
```solidity
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
});
```
This limit is likely too restrictive for normal application usage, especially for active users or scenarios where multiple users might share the same IP (such as corporate networks or NAT). This can lead to legitimate users being unable to access the service, resulting in a self-imposed denial of service.

## Recommendation
Increase the rate limit to a more reasonable value (e.g., 500-1000 requests per 10 minutes). Consider implementing more granular rate limits for specific endpoints rather than a global limit.

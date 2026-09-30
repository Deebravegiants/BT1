# [H] Global connection limit vulnerable to DoS attacks

## Summary
Severity: High
Contest weight: 0.1458
Dataset id: 6949
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The application implements a global connection limit in the connections.ts middleware: private static readonly MAX_ACTIVE_CONNECTIONS = 1000 While limiting connections is a good practice, the current implementation tracks connections globally rather (DoS) attack by creating multiple connections until the maximum limit is reached, preventing legitimate users from connecting. The lack of per-IP rate limiting at this layer makes it trivial for a malicious actor to consume all available connection slots.

## Recommendation
Implement per-IP connection limits instead. Consider relying on Cloudflare or similar WAF for rate limiting purposes.

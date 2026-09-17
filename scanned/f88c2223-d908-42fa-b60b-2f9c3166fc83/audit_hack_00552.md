# [H] Trust Wallet incident: Trust Wallet has issued an official notice confirming that version 2.68 of its browser extension contains a security vulnerability

## Summary
Severity: High
Target: Trust Wallet
Loss: $ 8,500,000
Attack method: Malicious Code Injection Attack
Published: 2025-12-26
Source: https://x.com/TrustWallet/status/2006029258209005699
Type: slowmist-incident

## Details
Trust Wallet has issued an official notice confirming that version 2.68 of its browser extension contains a security vulnerability, and advised all users running version 2.68 to immediately disable it and upgrade to version 2.69. According to SlowMist’s analysis, this backdoor incident originated from a malicious modification of Trust Wallet’s internal codebase (analytics service logic), rather than the introduction of a compromised third-party package (e.g., a malicious npm package). The attacker directly tampered with the application’s own code, using the legitimate PostHog library to redirect analytics data to a malicious server. As of December 31, the incident has been confirmed to affect 2,520 wallet addresses, with a total loss of approximately USD 8.5 million. Preliminary investigation indicates that this attack is related to the Sha1-Hulud industry-level supply chain incident that occurred in November. Trust Wallet has now rolled back the extension to the secure version 2.69 and initiated a compensation process for affected users.

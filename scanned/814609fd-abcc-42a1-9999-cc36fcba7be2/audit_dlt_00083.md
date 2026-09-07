# [H] Modified package published to npm, containing malware that exfiltrates private key material

## Summary
Severity: High
Chain: Solana
Component: solana-labs/solana-web3.js
CVE: CVE-2024-54134
CWE: Exposure of Sensitive Information to an Unauthorized Actor
Published: 2024-12-04
Source: https://github.com/solana-foundation/solana-web3.js/security/advisories/GHSA-jcxm-7wvp-g6p5
Type: github-advisory

## Details
Earlier today, a publish-access account was compromised for `@solana/web3.js`, a JavaScript library that is commonly used by Solana dapps. This allowed an attacker to publish unauthorized and malicious packages that were modified, allowing them to steal private key material and drain funds from dapps, like bots, that handle private keys directly. This issue should not affect non-custodial wallets, as they generally do not expose private keys during transactions. This is not an issue with the Solana protocol itself, but with a specific JavaScript client library and only appears to affect projects that directly handle private keys and that updated within the window of 3:20pm UTC and 8:25pm UTC on Tuesday, December 3, 2024.

These two unauthorized versions (1.95.6 and 1.95.7) were caught within hours and have since been unpublished.

We are asking all Solana app developers to upgrade to version 1.95.8. Developers pinned to `latest` should also upgrade to 1.95.8.

Developers that suspect they might be compromised should rotate any suspect authority keys, including multisigs, program authorities, server keypairs, and so on.

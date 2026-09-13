# [H] Handling untrusted input can result in a crash, leading to loss of availability / denial of service

## Summary
Severity: High
Chain: Solana
Component: solana-labs/solana-web3.js
CVE: CVE-2024-30253
Published: 2024-04-17
Source: https://github.com/solana-foundation/solana-web3.js/security/advisories/GHSA-8m45-2rjm-j347
Type: github-advisory

## Details
Using particular inputs with `@solana/web3.js` will result in memory exhaustion (OOM).

If you have a server, client, mobile, or desktop product that accepts untrusted input for use with one of the affected versions of `@solana/web3.js`, your application/service may crash, resulting in a loss of availability. Upgrade to a patched version.

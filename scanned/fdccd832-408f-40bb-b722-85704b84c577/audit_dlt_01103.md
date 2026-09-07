# [C] Compromised xrpl.js versions 4.2.1, 4.2.2, 4.2.3, 4.2.4, and 2.14.2

## Summary
Severity: Critical
Chain: xrpl
Component: xrpl, xrpl
CVE: CVE-2025-32965
CWE: Embedded Malicious Code
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-33qr-m49q-rxfx
Type: github-advisory

## Details
### Impact
Versions 4.2.1, 4.2.2, 4.2.3, and 4.2.4 of xrpl.js were compromised and contained malicious code designed to exfiltrate private keys. If you are using one of these versions, stop immediately and rotate any private keys or secrets used with affected systems.

Version 2.14.2 is also malicious, though it is less likely to lead to exploitation as it is not compatible with other 2.x versions.

### Patches
Upgrade to version 4.2.5 or 2.14.3.

### Required Actions
To secure funds, think carefully about whether any keys may have been compromised by this supply chain attack, and mitigate by sending funds to secure wallets, and/or rotating keys:

The XRP Ledger supports key rotation: https://xrpl.org/docs/tutorials/how-tos/manage-account-settings/assign-a-regular-key-pair

If any account's master key is potentially compromised, you should disable it: https://xrpl.org/docs/tutorials/how-tos/manage-account-settings/disable-master-key-pair

### References
https://www.aikido.dev/blog/xrp-supplychain-attack-official-npm-package-infected-with-crypto-stealing-backdoor

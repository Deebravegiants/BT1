# [M] Safuwallet incident: ZenGo co-founder Ouriel Ohayon reported on Twitter that the wallet extension SAFU Wallet apparently steals large amounts of money

## Summary
Severity: Medium
Target: Safuwallet
Loss: -
Attack method: Malicious Code Injection Attack
Published: 2019-10-11
Source: https://cryptonews.net/news/security/226480/
Type: slowmist-incident

## Details
ZenGo co-founder Ouriel Ohayon reported on Twitter that the wallet extension SAFU Wallet apparently steals large amounts of money by injecting malicious code into users. A white hat hacker said that by inspecting the SAFU code, he found that they dynamically injected this script https://safuwallet.tk/inside.js in every page being loaded. At the same time, they use obfuscation tools to make it hard to see. Nonetheless, the white hat hackers explained that they targeted MEW, Index and Binance, using background scripts to send information to 4 different endpoints on the same domain. Therefore, the created wallet is automatically shared with them. Currently, the SAFU Wallet Google Chrome website is not available after a community request to remove the extension.

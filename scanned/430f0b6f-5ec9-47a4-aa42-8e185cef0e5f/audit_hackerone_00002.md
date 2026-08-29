# [M] View-only offline transaction creation bypasses the long-payment-ID privacy block

## Summary
Severity: Medium (CVSS 5.4)
Program: Monero
Weakness: Information Disclosure
Reporter: qttps
State: resolved
Disclosed: 2026-08-20T23:49:45.868Z
Source: https://hackerone.com/reports/3686283

## Details
## Summary
The monero-gui Transfer page correctly blocks the normal online "Send" action when a standalone payment ID is present. The warning shown to the user states that long payment IDs are obsolete, were not encrypted on-chain, and harm privacy.

However, the view-only offline transaction signing flow does not enforce the same protection. In a view-only wallet, the "Offline transaction signing" -> "Create" button remains enabled even when the long-payment-ID warning is visible. That offline Create action forwards the same `paymentIdLine.text` value into the shared transaction creation handler and then into the C++ wallet backend transaction creation API.

This means a QR code, `monero:` URI, or manually entered payment request can include a standalone payment ID that blocks normal Send, but still allows creation of an unsigned offline transaction. If the unsigned transaction is later signed and submitted, the unencrypted payment ID can link or identify the user's payment on-chain.

## Weakness

Protection Mechanism Failure, CWE-693.

A secondary classification may be CWE-200 because the impact is privacy exposure through transaction metadata.

## Severity

Suggested CVSS 3.0:

`CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N`

Suggested severity: Medium.

## Affected Component

monero-gui transaction creation flow:

- `pages/Transfer.qml`
- `main.qml`
- `components/QRCodeScanner.qml`
- `components/TxConfirmationDialog.qml`
- `src/libwalletqt/Wallet.cpp`
- `src/libwalletqt/WalletManager.cpp`

The exact release version is not inferable from my local checkout because it does not include Git metadata. The issue is present in the reviewed monero-gui source tree.

## Technical Details

Untrusted payment data can enter the GUI through a `monero:` URI or QR code.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3686283_

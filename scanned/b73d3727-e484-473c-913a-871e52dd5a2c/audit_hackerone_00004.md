# [M] monero:// deeplink parsing accepts tx_amount=(all) and can trigger send-all transaction mode

## Summary
Severity: Medium (CVSS 6.5)
Program: Monero
Weakness: Business Logic Errors
Reporter: qttps
State: resolved
Disclosed: 2026-08-20T23:47:45.348Z
Source: https://hackerone.com/reports/3648638

## Details
## Summary

Monero GUI has two different URI ingestion paths.

QR/manual URI handling uses the canonical backend parser, but external `monero://` deeplinks are parsed by a separate QML routine in `main.qml`. That deeplink path forwards the raw `tx_amount` string into the transfer model without canonical numeric validation.

The transfer model reserves the literal string `"(all)"` as a privileged internal control value meaning "send all unlocked balance". Because the external deeplink path does not reject that sentinel, an attacker can supply a crafted URI such as:

`monero://<attacker_address>?tx_amount=(all)&tx_description=test`

and the wallet will enter the send-all transaction path for the attacker-controlled address.

## Releases Affected

Observed in the current Monero GUI source checkout corresponding to `0.18.4.6`.

Affected code paths:
- `main.qml:447-478`
- `pages/Transfer.qml:95-105`
- `pages/Transfer.qml:203-212`
- `main.qml:964-980`

Comparison path showing the stricter canonical parser:
- `src/libwalletqt/WalletManager.cpp:406-423`

## Steps To Reproduce

1. Inspect `main.qml:447-478`.
   `onUriHandler(uri)` manually parses `monero://` query parameters and forwards raw `params["tx_amount"]` into `middlePanel.transferView.sendTo(...)`.

2. Inspect `pages/Transfer.qml:95-105`.
   `fillPaymentDetails(...)` inserts the attacker-controlled amount into `recipientModel` via:
   `recipientModel.newRecipient(address, Utils.removeTrailingZeros(amount || ""))`
   There is no numeric validation here.

3. Inspect `pages/Transfer.qml:203-212`.
   `recipientModel.getAmountTotal()` treats the exact literal `"(all)"` as a special internal value and returns the wallet's unlocked balance.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3648638_

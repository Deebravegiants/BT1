# [M] Monero GUI OpenAlias DNSSEC-invalid resolution still writes spoofable address into recipient field

## Summary
Severity: Medium
Program: Monero
Weakness: N/A
Reporter: lilpeko
State: resolved
Disclosed: 2026-08-20T23:51:18.358Z
Source: https://hackerone.com/reports/3819475

## Details
## Summary:
Monero GUI resolves OpenAlias names through DNS and exposes the DNSSEC result to QML as `true|address` or `false|address`. When DNSSEC validation fails but the TXT record contains a syntactically valid Monero address, `TxUtils.handleOpenAliasResolution()` returns both a warning message and the resolved address. The Transfer and Address Book pages then apply `response.address` to the recipient field even though `response.message` says the address may be spoofed.

Impact summary: an attacker who can influence a victim's DNS/OpenAlias lookup can make the GUI's OpenAlias helper produce an attacker-controlled address despite failed DNSSEC validation. The QML transfer flow then writes that unauthenticated address into the recipient field. If the victim proceeds with the send flow, funds are sent to the attacker-controlled address.

## Affected Code & Version

Repository/version reviewed:

- `monero-gui` commit `003e667576f38812e27cbb79125a0ba96036225d` on `master`
- CLI/library source reviewed from `/home/peko/monero/monero` commit `2c48374ecd2449c02bb400e5bcf20b7c6f11649b`

Affected code:

- `monero-gui/src/libwalletqt/WalletManager.cpp:391-396`
  - `WalletManager::resolveOpenAlias()` serializes the resolver result as `dnssec_valid ? "true" : "false"` plus the resolved address.
- `monero/src/wallet/api/wallet_manager.cpp:338-344`
  - `WalletManagerImpl::resolveOpenAlias()` returns the first address from `tools::dns_utils::addresses_from_url()` even when `dnssec_valid` is false.
- `monero/src/common/dns_utils.cpp:418-442`
  - `addresses_from_url()` sets `dnssec_valid = false` unless DNSSEC is both available and valid, but still returns parsed OpenAlias addresses from TXT records.
- `monero-gui/js/TxUtils.js:82-105`
  - For `isDnssecValid === "false"` and `isAddressValid`, `handleOpenAliasResolution()` returns `{ address: resolvedAddress, message: "..." }` instead of withholding the address.
- `monero-gui/pages/Transfer.qml:430-438`
  - The Transfer page shows the warning, then unconditionally writes `response.address` into the recipient field.
- `monero-gui/pages/AddressBook.qml:389-397`
  - The Address Book page has the same pattern and persists the spoofable address if the user saves the entry.

Relevant CLI comparison:

- `monero/src/simplewallet/simplewallet.cpp:501-534`
  - The CLI path prompts for explicit confirmation and displays DNSSEC status before returning the address. The GUI path does not require a confirm/deny decision before writing the address into the payment form.


## Steps to Reproduce

The lab PoC below does not query live DNS, does not open a wallet, does not relay transactions, and does not touch the Monero network. It executes the actual `monero-gui/js/TxUtils.js` source with mocked QML globals and then applies the same recipient-field assignment performed by `Transfer.qml`.

1. On the lab VM, run the PoC Script:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3819475_

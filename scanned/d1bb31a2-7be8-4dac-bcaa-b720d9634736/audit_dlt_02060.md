# [?] fix: session approval race condition (#2395)

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2023-05-17
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/6ef2258ea039a9fb7b8162a47a6ed8cf6571b6c1
Type: security-commit

## Details
fix: session approval race condition (#2395)

* fix: adds 500ms delay on session approval to avoid race condition where the peer hasn't finished processing the proposal while receiving requests

* chore: log incoming payloads

* chore: log pairing pings

* chore: lint

* chore: log pairing ack

* chore: pairing event

* chore: log pairing event emit

* chore: remove logs

---------

Co-authored-by: Gancho Radkov <ganchoradkov@gmail.com>

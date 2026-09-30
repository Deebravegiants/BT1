# [?] Fix panic when no instance is passed to certain CLI options (#275)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2020-08-07
Source: https://github.com/paritytech/polkadot-sdk/commit/acb78b0595f9c5960aee24fcf974563da8baf698
Type: security-commit

## Details
Fix panic when no instance is passed to certain CLI options (#275)

## Patch
### bridges/relays/ethereum/src/cli.yml
```diff
@@ -85,6 +85,7 @@ subcommands:
                 help: Hex-encoded secret to use when transactions are submitted to the Ethereum node.
             - sub-host: *sub-host
             - sub-port: *sub-port
+            - sub-pallet-instance: *sub-pallet-instance
             - no-prometheus: *no-prometheus
             - prometheus-host: *prometheus-host
             - prometheus-port: *prometheus-port
@@ -102,6 +103,7 @@ subcommands:
                 takes_value: true
             - sub-host: *sub-host
             - sub-port: *sub-port
+            - sub-pallet-instance: *sub-pallet-instance
             - sub-authorities-set-id:
                 long: sub-authorities-set-id
                 value_name: SUB_AUTHORITIES_SET_ID
@@ -160,6 +162,7 @@ subcommands:
             - sub-port: *sub-port
             - sub-signer: *sub-signer
             - sub-signer-password: *sub-signer-password
+            - sub-pallet-instance: *sub-pallet-instance
             - no-prometheus: *no-prometheus
             - prometheus-host: *prometheus-host
             - prometheus-port: *prometheus-port
```

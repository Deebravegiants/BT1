# [?] [fix]: Fix clap panic on parsing relayer commands

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-09-24
Source: https://github.com/namada-net/namada/commit/d44597fd029f4173b11846d6778645236ecb85e3
Type: security-commit

## Details
[fix]: Fix clap panic on parsing relayer commands

## Patch
### crates/apps_lib/src/cli.rs
```diff
@@ -75,10 +75,8 @@ pub mod cmds {
     impl Cmd for Namada {
         fn add_sub(app: App) -> App {
             app.subcommand(NamadaNode::def().display_order(1))
-                // .subcommand(NamadaRelayer::def().display_order(1))
                 .subcommand(NamadaClient::def().display_order(1))
                 .subcommand(NamadaWallet::def().display_order(1))
-                // .subcommand(EthBridgePool::def().display_order(2))
                 .subcommand(Ledger::def().display_order(2))
                 .subcommand(TxCustom::def().display_order(2))
                 .subcommand(TxTransparentTransfer::def().display_order(2))
@@ -96,9 +94,6 @@ pub mod cmds {
         fn parse(matches: &ArgMatches) -> Option<Self> {
             let node = SubCmd::parse(matches).map(Self::Node);
             let client = SubCmd::parse(matches).map(Self::Client);
-            let relayer = SubCmd::parse(matches).map(Self::Relayer);
-            let eth_bridge_pool =
-                SubCmd::parse(matches).map(Self::EthBridgePool);
             let wallet = SubCmd::parse(matches).map(Self::Wallet);
             let ledger = SubCmd::parse(matches).map(Self::Ledger);
             let tx_custom = SubCmd::parse(matches).map(Self::TxCustom);
@@ -121,8 +116,6 @@ pub mod cmds {
             let tx_reveal_pk = SubCmd::parse(matches).map(Self::TxRevealPk);
             let complete = SubCmd::parse(matches).map(Self::Complete);
             node.or(client)
-                .or(relayer)
-                .or(eth_bridge_pool)
                 .or(wallet)
                 .or(ledger)
                 .or(tx_custom)
```

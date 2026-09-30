# [?] fix: remove panics on bitcoin broadcaster (#3568)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2023-07-03
Source: https://github.com/chainflip-io/chainflip-backend/commit/bafa368ea298a48a2d329c76559364baaf28b229
Type: security-commit

## Details
fix: remove panics on bitcoin broadcaster (#3568)

## Patch
### state-chain/runtime/src/chainflip.rs
```diff
@@ -402,15 +402,15 @@ impl BroadcastAnyChainGovKey for TokenholderGovernanceBroadcaster {
 				Self::broadcast_gov_key::<Ethereum, EthereumBroadcaster>(maybe_old_key, new_key),
 			ForeignChain::Polkadot =>
 				Self::broadcast_gov_key::<Polkadot, PolkadotBroadcaster>(maybe_old_key, new_key),
-			ForeignChain::Bitcoin => todo!("Bitcoin govkey broadcast"),
+			ForeignChain::Bitcoin => Err(()),
 		}
 	}
 
 	fn is_govkey_compatible(chain: ForeignChain, key: &[u8]) -> bool {
 		match chain {
 			ForeignChain::Ethereum => Self::is_govkey_compatible::<Ethereum>(key),
 			ForeignChain::Polkadot => Self::is_govkey_compatible::<Polkadot>(key),
-			ForeignChain::Bitcoin => todo!("Bitcoin govkey compatibility"),
+			ForeignChain::Bitcoin => false,
 		}
 	}
 }
```

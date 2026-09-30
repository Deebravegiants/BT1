# [?] Provide initial Shelley credentials (unsound credentials)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/cardano-node
Published: 2025-09-26
Source: https://github.com/IntersectMBO/cardano-node/commit/5dc89d6083765fc8a4b30b5545d5f0a4c53458c7
Type: security-commit

## Details
Provide initial Shelley credentials (unsound credentials)

## Patch
### cardano-node/src/Cardano/Node/Protocol/Shelley.hs
```diff
@@ -39,7 +39,7 @@ import           Cardano.Protocol.Crypto (StandardCrypto)
 import           Cardano.Tracing.OrphanInstances.HardFork ()
 import           Cardano.Tracing.OrphanInstances.Shelley ()
 import qualified Ouroboros.Consensus.Cardano as Consensus
-import           Ouroboros.Consensus.Protocol.Praos.Common (PraosCanBeLeader (..))
+import           Ouroboros.Consensus.Protocol.Praos.Common (PraosCanBeLeader (..), PraosCredentialsSource (..))
 import           Ouroboros.Consensus.Shelley.Node (Nonce (..), ProtocolParamsShelleyBased (..),
                    ShelleyLeaderCredentials (..))
 
@@ -261,8 +261,7 @@ mkPraosLeaderCredentials
         PraosCanBeLeader {
           praosCanBeLeaderColdVerKey = coerceKeyRole vkey,
           praosCanBeLeaderSignKeyVRF = vrfKey,
-          -- TODO: fix
-          praosCanBeLeaderCredentialsSource = undefined
+          praosCanBeLeaderCredentialsSource = PraosCredentialsUnsound opcert kesKey
         },
       shelleyLeaderCredentialsLabel = "Shelley"
     }
```

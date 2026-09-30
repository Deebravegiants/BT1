# [?] [Bug] Fix SPV Test Nondeterminism (#210)

## Summary
Severity: Unknown
Chain: Kadena
Component: kadena-io/chainweb-node
Published: 2019-05-28
Source: https://github.com/kadena-io/chainweb-node/commit/5757151e355a58d7cb51b680645a278851c36587
Type: security-commit

## Details
[Bug] Fix SPV Test Nondeterminism (#210)

* make SPV tests deterministic by massaging mining bounds

## Patch
### src/Chainweb/Pact/SPV.hs
```diff
@@ -22,6 +22,7 @@ module Chainweb.Pact.SPV
 import GHC.Stack
 
 import Control.Concurrent.MVar
+import Control.Error
 import Control.Lens hiding (index)
 import Control.Monad.Catch
 
@@ -42,6 +43,7 @@ import Chainweb.BlockHeaderDB
 import Chainweb.CutDB (CutDb)
 import Chainweb.Pact.Service.Types
 import Chainweb.Pact.Types
+import Chainweb.Pact.Utils (aeson)
 import Chainweb.Payload
 import Chainweb.Payload.PayloadStore
 import Chainweb.SPV
@@ -70,22 +72,20 @@ pactSPV cdbv l = SPVSupport $ \s o -> readMVar cdbv >>= go s o
   where
     -- extract spv resources from pact object
     go s o cdb = case s of
-      "TXOUT" -> txOutputProofOf o >>= \case
-          Left e -> spvError e
-          Right t -> verifyTransactionOutputProof cdb t
-            >>= extractOutputs
-      "TXIN" -> spvError "TXIN is currently unsupported"
-      x -> spvError
+      "TXOUT" -> case txOutputProofOf o of
+        Left u -> return $ Left u
+        Right t -> extractOutputs =<< verifyTransactionOutputProof cdb t
+      "TXIN" -> return $ Left "TXIN is currently unsupported"
+      x -> return . Left
         $ "TXIN or TXOUT must be specified to generate valid spv proofs: "
         <> x
 
-    txOutputProofOf :: Object Name -> IO (Either Text (TransactionOutputProof SHA512t_256))
-    txOutputProofOf o =
-      case toPactValue $ TObject o def of
-        Left e -> spvError e
-        Right t -> case fromJSON . toJSON $ t of
-          Error e -> spvError' e
-          Success u -> return $ Right u
+    txOutputProofOf
+        :: Object Name
+        -> Either Text (TransactionOutputProof SHA512t_256)
+    txOutputProofOf o = k =<< toPactValue (TObject o def)
+      where
+        k = aeson (Left . pack) Right . fromJSON . toJSON
 
     extractOutputs :: TransactionOutput -> IO (Either Text (Object Name))
     extractOutputs (TransactionOutput t) =
@@ -96,10 +96,10 @@ pactSPV cdbv l = SPVSupport $ \s o -> readMVar cdbv >>= go s o
           (TObject o _) -> return $ Right o
           o -> do
             logLog l "ERROR" $ show o
-            spvError' "type error in associated pact transaction, should be object"
+            return . Left $ pack "type error in associated pact transaction, should be object"
         Just o -> do
           logLog l "ERROR" $ show o
-          spvError' "Invalid command result in associated pact output"
+          return . Left $ pack "Invalid command result in associated pact output"
 
 
 -- | Look up pact tx hash at some block height in the
@@ -118,9 +118,8 @@ getTxIdx
 getTxIdx bdb pdb bh th = do
     -- get BlockPayloadHash
     ph <- fmap (fmap _blockPayloadHash)
-        $ entries bdb Nothing (Just 1) (Just $ int bh) Nothing S.head_ >>= \case
-            Nothing -> spvError "unable to find payload associated with transaction hash"
-            Just x -> return $ Right x
+        $ entries bdb Nothing (Just 1) (Just $ int bh) Nothing S.head_
+        >>= pure . note "unable to find payload associated with transaction hash"
 
     case ph of
       Left s -> return $ Left s
@@ -134,9 +133,9 @@ getTxIdx bdb pdb bh th = do
           & S.mapM toTxHash
           & sindex (== th)
 
-        case r of
-          Nothing -> spvError "unable to find transaction at the given block height"
-          Just x -> return $ Right (int x)
+        r & note "unable to find transaction at the given block height"
+          & fmap int
+          & return
   where
     toPactTx :: MonadThrow m => Transaction -> m (Command Text)
     toPactTx (Transaction b) = decodeStrictOrThrow b
@@ -149,14 +148,3 @@ getTxIdx bdb pdb bh th = do
 
     sindex :: Monad m => (a -> Bool) -> S.Stream (S.Of a) m () -> m (Maybe Natural)
     sindex p s = S.zip (S.each [0..]) s & sfind (p . snd) & fmap (fmap fst)
-
--- -------------------------------------------------------------------------- --
--- utilities
-
--- | Prepend "spvSupport" to any errors so we can differentiate messages
---
-spvError :: Text -> IO (Either Text a)
-spvError = return . Left . (<>) "spvSupport: "
-
-spvError' :: String -> IO (Either Text a)
-spvError' = spvError . pack
```

### src/Chainweb/Pact/Utils.hs
```diff
@@ -10,16 +10,22 @@
 -- Pact service for Chainweb
 
 module Chainweb.Pact.Utils
-    ( toEnv'
+    ( -- * persistence
+      toEnv'
     , toEnvPersist'
+      -- * combinators
+    , aeson
     ) where
 
+import Data.Aeson
+
 import Control.Concurrent.MVar
 
 import Pact.Interpreter as P
 
 import Chainweb.Pact.Types
 
+
 toEnv' :: EnvPersist' -> IO Env'
 toEnv' (EnvPersist' ep') = do
     let thePactDb = _pdepPactDb $! ep'
@@ -36,3 +42,10 @@ toEnvPersist' (Env' pactDbEnv) = do
           , _pdepEnv = dbEnv
           }
     return $! EnvPersist' pDbEnvPersist
+
+-- | This is the recursion principle of an 'Aeson' 'Result' of type 'a'.
+-- Similar to 'either', 'maybe', or 'bool' combinators
+--
+aeson :: (String -> b) -> (a -> b) -> Result a -> b
+aeson f _ (Error a) = f a
+aeson _ g (Success a) = g a
```

### test/Chainweb/Test/CutDB.hs
```diff
@@ -1,4 +1,5 @@
 {-# LANGUAGE AllowAmbiguousTypes #-}
+{-# LANGUAGE BangPatterns #-}
 {-# LANGUAGE FlexibleContexts #-}
 {-# LANGUAGE LambdaCase #-}
 {-# LANGUAGE OverloadedStrings #-}
@@ -35,7 +36,9 @@ import Control.Concurrent.Async
 import Control.Concurrent.STM as STM
 import Control.Lens hiding (elements)
 import Control.Monad
+import Control.Monad.Catch
 
+import Data.Foldable
 import Data.Function
 import qualified Data.Sequence as Seq
 import Data.Tuple.Strict
@@ -196,7 +199,17 @@ extendAwait cdb pact i p = race gen (awaitCut cdb p) >>= \case
     Left _ -> return Nothing
     Right c -> return (Just c)
   where
-    gen = void $! S.effects $ extendTestCutDb cdb pact i
+    gen = void
+        $ S.foldM_ checkCut (return 0) return
+        $ S.map (view (_1 . cutHeight))
+        $ extendTestCutDb cdb pact i
+
+    checkCut prev cur = do
+        unless (prev < cur) $ throwM $ InternalInvariantViolation $ unexpectedMsg
+            "New cut is not larger than the previous one. This is bug in Chainweb.Test.CutDB"
+            (Expected prev)
+            (Actual cur)
+        return cur
 
 -- | Wait for the cutdb to produce at least one new cut, that is different from
 -- the given cut.
@@ -207,6 +220,9 @@ awaitNewCut
     -> IO Cut
 awaitNewCut cdb = awaitCut cdb . (/=)
 
+-- | Wait for the cutdb to synchronize on a given blockheight for a given chain
+-- id
+--
 awaitBlockHeight
     :: CutDb cas
     -> BlockHeight
@@ -317,8 +333,8 @@ startLocalPayloadStore mgr payloadDb = do
     mem <- new
     return $ (server, WebBlockPayloadStore payloadDb mem queue (\_ _ -> return ()) mgr fakePact)
 
--- | Build a linear chainweb (no forks). No POW or poison delay is applied.
--- Block times are real times.
+-- | Build a linear chainweb (no forks, assuming single threaded use of the
+-- cutDb). No POW or poison delay is applied. Block times are real times.
 --
 mine
     :: HasCallStack
@@ -332,15 +348,39 @@ mine
     -> Cut
     -> IO (Cut, ChainId, PayloadWithOutputs)
 mine miner pact cutDb c = do
-    -- pick chain
-    cid <- randomChainId cutDb
+
+    -- Pick a chain that isn't blocked. With that mining is guaranteed to
+    -- succeed if
+    --
+    -- * there are no other writers to the cut db,
+    -- * the chainweb is in a consistent state,
+    -- * the pact execution service is synced with the cutdb, and
+    -- * the transaction generator produces valid blocks.
+    cid <- getRandomUnblockedChain c
 
     tryMine miner pact cutDb c cid >>= \case
-        Left _ -> mine miner pact cutDb c
+        Left _ -> throwM $ InternalInvariantViolation
+            "Failed to create new cut. This is a bug in Test.Chainweb.CutDB or one of it's users"
         Right x -> do
-            void $ awaitCut cutDb $ ((>=) `on` _cutHeight) (view _1 x)
+            void $ awaitCut cutDb $ ((<=) `on` _cutHeight) (view _1 x)
             return x
 
+-- | Return a random chain id from a cut that is not blocked.
+--
+getRandomUnblockedChain :: Cut -> IO ChainId
+getRandomUnblockedChain c = do
+    shuffled <- generate $ shuffle $ toList $ _cutMap c
+    S.each shuffled
+        & S.filter isUnblocked
+        & S.map _blockChainId
+        & S.head_
+        & fmap fromJuste
+  where
+    isUnblocked h =
+        let bh = _blockHeight h
+            cid = _blockChainId h
+        in all (>= bh) $ fmap _blockHeight $ toList $ cutAdjs c cid
+
 -- | Build a linear chainweb (no forks). No POW or poison delay is applied.
 -- Block times are real times.
 --
```

### test/Chainweb/Test/Pact/PactInProcApi.hs
```diff
@@ -37,6 +37,7 @@ import Test.Tasty.HUnit
 
 -- internal modules
 
+import Chainweb.BlockHash
 import Chainweb.BlockHeader
 import Chainweb.BlockHeader.Genesis
 import Chainweb.ChainId
@@ -155,8 +156,11 @@ testMemPoolAccess _bHeight _bHash _bHeader = do
 
 
 testEmptyMemPool
-  :: p1 -> p2 -> p3 -> IO (V.Vector ChainwebTransaction)
-testEmptyMemPool _bHeight _bHash _bHeader = goldenTestTransactions V.empty
+    :: BlockHeight
+    -> BlockHash
+    -> BlockHeader
+    -> IO (V.Vector ChainwebTransaction)
+testEmptyMemPool _ _ _ = goldenTestTransactions V.empty
 
 testLocal :: IO ChainwebTransaction
 testLocal = do
```

### test/Chainweb/Test/Pact/SPV.hs
```diff
@@ -19,11 +19,17 @@
 -- Pact Service SPV Support roundtrip tests
 --
 module Chainweb.Test.Pact.SPV
-( tests
+( -- * test suite
+  tests
+  -- * repl tests
+, standard
+, wrongchain
+, badproof
+, doublespend
 ) where
 
 import Control.Concurrent.MVar (MVar, readMVar, newMVar)
-import Control.Exception (SomeException, finally)
+import Control.Exception (SomeException, finally, throwIO)
 import Control.Lens hiding ((.=))
 import Control.Monad.Catch (catch)
 
@@ -32,6 +38,8 @@ import Data.Default
 import Data.Function
 import Data.Functor (void)
 import Data.IORef
+import Data.List (isInfixOf)
+import Data.Text (pack)
 import qualified Data.Text.IO as T
 import Data.Vector (Vector, fromList)
 
@@ -91,34 +99,50 @@ gorder = int . order . _chainGraph $ v
 height :: Chainweb.ChainId -> Cut -> BlockHeight
 height cid c = _blockHeight $ c ^?! ixg cid
 
-handle :: SomeException -> IO Bool
-handle _ = return False
+handle :: SomeException -> IO (Bool, String)
+handle e = return (False, show e)
 
--- expected failures take this form
-expectedFailure :: IO Bool -> String -> Assertion
-expectedFailure test msg = do
-    b <- catch test handle
-    assertBool ("Unexpected success: " <> msg <> " should fail") (not b)
+-- debugging
+_handle' :: SomeException -> IO (Bool, String)
+_handle' e =
+    let
+      s = show e
+    in logg System.LogLevel.Error (pack s) >> return (False, s)
 
-expectedSuccess :: IO Bool -> String -> Assertion
-expectedSuccess test msg = do
-    b <- catch test handle
-    assertBool ("Unexpected failure: " <> msg <> " should succeed") b
+-- | expected failures take this form.
+--
+expectFailure :: String -> IO (Bool, String) -> Assertion
+expectFailure err test = do
+    (b, s) <- catch test handle
+    if err `isInfixOf` s then
+      assertBool "Unexpected success" $ not b
+    else throwIO $ userError s
+
+
+-- | expected successes take this form
+--
+expectSuccess :: IO (Bool, String) -> Assertion
+expectSuccess test = do
+    (b, s) <- catch test handle
+    assertBool ("Unexpected failure: " <> s) b
 
 -- -------------------------------------------------------------------------- --
 -- tests
 
 standard :: Assertion
-standard = expectedSuccess (roundtrip 0 1 txGenerator1 txGenerator2) "round trip"
+standard = expectSuccess $ roundtrip 0 1 txGenerator1 txGenerator2
 
 doublespend :: Assertion
-doublespend = expectedFailure (roundtrip 0 1 txGenerator1 txGenerator3) "double spend"
+doublespend = expectFailure "Tx Failed: enforce unique usage" $
+    roundtrip 0 1 txGenerator1 txGenerator3
 
 wrongchain :: Assertion
-wrongchain = expectedFailure (roundtrip 0 1 txGenerator1 txGenerator4) "wrong chain execution"
+wrongchain = expectFailure "Tx Failed: enforce correct create chain ID" $
+    roundtrip 0 1 txGenerator1 txGenerator4
 
 badproof :: Assertion
-badproof = expectedFailure (roundtrip 0 1 txGenerator1 txGenerator5) "wrong proof format"
+badproof = expectFailure "SPV verify failed: key \"chain\" not present" $
+    roundtrip 0 1 txGenerator1 txGenerator5
 
 roundtrip
     :: Int
@@ -129,26 +153,28 @@ roundtrip
       -- ^ burn tx generator
     -> CreatesGenerator
       -- ^ create tx generator
-    -> IO Bool
-roundtrip _sid _tid burn create = do
+    -> IO (Bool, String)
+roundtrip sid0 tid0 burn create = do
     -- Pact service that is used to initialize the cut data base
     pact0 <- testWebPactExecutionService v Nothing (return mempty)
     withTempRocksDb "chainweb-sbv-tests"  $ \rdb ->
         withTestCutDb rdb v 20 pact0 logg $ \cutDb -> do
             cdb <- newMVar cutDb
 
-            sid <- mkChainId v _sid
-            tid <- mkChainId v _tid
+            sid <- mkChainId v sid0
+            tid <- mkChainId v tid0
 
             -- pact service, that is used to extend the cut data base
-            pact1 <- testWebPactExecutionService v (Just cdb) $ burn tid
+            txGen1 <- burn sid tid
+            pact1 <- testWebPactExecutionService v (Just cdb) txGen1
             syncPact cutDb pact1
 
             c0 <- _cut cutDb
 
             -- get tx output from `(coin.delete-coin ...)` call.
             -- Note: we must mine at least (diam + 1) * graph order many blocks
             -- to ensure we synchronize the cutdb across all chains
+
             c1 <- fmap fromJuste $ extendAwait cutDb pact1 ((diam + 1) * gorder) $
                 ((<) `on` height sid) c0
 
@@ -163,27 +189,27 @@ roundtrip _sid _tid burn create = do
             -- randomly you mine another 2 * diameter(graph) * 10 = 40 blocks to
             -- make up for uneven height distribution.
 
-            -- So in total you would add 60 blocks which would guarantee that
+            -- So in total you would add 60 + 2 blocks which would guarantee that
             -- all chains advanced by at least 2 blocks. This is probably an
             -- over-approximation, I guess the formula could be made a little
             -- more tight, but the that’s the overall idea. The idea behind the
             -- `2 * diameter(graph) * order(graph)` corrective is that, the
             -- block heights between any two chains can be at most
             -- `diameter(graph)` apart.
 
-            c2 <- fmap fromJuste $ extendAwait cutDb pact1 60 $ \c ->
-                height tid c > diam + height tid c0
+            c2 <- fmap fromJuste $ extendAwait cutDb pact1 80 $ \c ->
+                height tid c > diam + height sid c1
 
             -- execute '(coin.create-coin ...)' using the  correct chain id and block height
             txGen2 <- create cdb sid tid (height sid c1)
             pact2 <- testWebPactExecutionService v (Just cdb) txGen2
             syncPact cutDb pact2
 
             -- consume the stream and mine second batch of transactions
-            void $ extendAwait cutDb pact2 (diam * gorder)
-                $ ((<) `on` height tid) c2
+            void $ fmap fromJuste $ extendAwait cutDb pact2 ((diam + 1) * gorder) $
+                ((<) `on` height tid) c2
 
-            return True
+            return (True, "test succeeded")
 
 -- -------------------------------------------------------------------------- --
 -- transaction generators
@@ -192,21 +218,32 @@ type TransactionGenerator
     = Chainweb.ChainId -> BlockHeight -> BlockHash -> BlockHeader -> IO (Vector ChainwebTransaction)
 
 type BurnGenerator
-    = Chainweb.ChainId -> TransactionGenerator
+    = Chainweb.ChainId -> Chainweb.ChainId -> IO TransactionGenerator
 
 type CreatesGenerator
     = MVar (CutDb RocksDbCas) -> Chainweb.ChainId -> Chainweb.ChainId -> BlockHeight -> IO TransactionGenerator
 
+
 -- | Generate burn/create Pact Service commands on arbitrarily many chains
 --
 txGenerator1 :: BurnGenerator
-txGenerator1 tid _cid _bhe _bha _ = do
-    ks <- testKeyPairs
+txGenerator1 sid tid = do
+    ref <- newIORef False
+    return $ go ref
+  where
+    go ref _cid _bhe _bha _
+      | sid /= _cid = return mempty
+      | otherwise = readIORef ref >>= \case
+        True -> return mempty
+        False -> do
+            ks <- testKeyPairs
 
-    let pcid = Pact.ChainId $ chainIdToText _cid
+            let pcid = Pact.ChainId $ chainIdToText _cid
+
+
+            mkPactTestTransactions "sender00" pcid ks "1" 100 0.0001 txs
+                `finally` writeIORef ref False
 
-    mkPactTestTransactions "sender00" pcid ks "1" 100 0.0001 txs
-  where
     txs = fromList [ PactTransaction tx1Code tx1Data ]
 
     tx1Code =
@@ -226,7 +263,8 @@ txGenerator1 tid _cid _bhe _bha _ = do
 
       in Just $ object
          [ "sender01-keyset" .= ks
-         , "target-chain-id" .= chainIdToText tid ]
+         , "target-chain-id" .= chainIdToText tid
+         ]
 
 -- | Generate the 'create-coin' command in response to the previous 'delete-coin' call.
 -- Note that we maintain an atomic update to make sure that if a given chain id
@@ -253,9 +291,7 @@ txGenerator2 cdbv sid tid bhe = do
                 mkPactTestTransactions "sender00" pcid ks "1" 100 0.0001 (txs q)
                     `finally` writeIORef ref True
 
-    txs q = fromList
-      [ PactTransaction tx1Code (tx1Data q)
-      ]
+    txs q = fromList [ PactTransaction tx1Code (tx1Data q) ]
 
     tx1Code =
       [text|
@@ -348,9 +384,7 @@ txGenerator5 _cdbv _ tid _ = do
                 mkPactTestTransactions "sender00" pcid ks "1" 100 0.0001 txs
                     `finally` writeIORef ref True
 
-    txs = fromList
-      [ PactTransaction tx1Code Nothing
-      ]
+    txs = fromList [ PactTransaction tx1Code Nothing ]
 
     tx1Code =
       [text|
```

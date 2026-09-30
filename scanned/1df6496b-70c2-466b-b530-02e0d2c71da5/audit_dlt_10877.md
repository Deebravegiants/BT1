# [?] Merge branch 'double-spend-signer' into 'master'

## Summary
Severity: Unknown
Chain: THORChain
Component: thorchain/thornode
Published: 2020-02-02
Source: https://github.com/thorchain/thornode/commit/569f03acf9f70d8f7ed98ddf6ca62a7faab0f62e
Type: security-commit

## Details
Merge branch 'double-spend-signer' into 'master'

[bugfix] improve defense against double spending

Closes #333

See merge request thorchain/thornode!537

## Patch
### bifrost/signer/sign.go
```diff
@@ -292,9 +292,11 @@ func (s *Signer) signTxOutAndSendToChain(txOut types.TxOut) error {
 	// most case , there should be only one item in txOut.TxArray, but sometimes there might be more than one
 	height := txOut.Height
 	for _, item := range txOut.TxArray {
-		processed, err := s.storage.HasTxOutItem(item, height)
+		key := item.GetKey(height)
+		processed, err := s.storage.HasTxOutItem(key)
 		if err != nil {
-			return fmt.Errorf("fail to check against local level db: %w", err)
+			s.logger.Error().Err(err).Msg("fail to check against local level db")
+			continue
 		}
 		if processed {
 			s.logger.Debug().Msgf("%+v processed already", item)
@@ -305,11 +307,17 @@ func (s *Signer) signTxOutAndSendToChain(txOut types.TxOut) error {
 			s.logger.Info().
 				Str("signer_address", s.Chain.GetAddress(item.VaultPubKey)).
 				Msg("different pool address, ignore")
+			if err := s.storage.ClearTxOutItem(key); err != nil {
+				s.logger.Error().Err(err).Msg("fail to mark it off from local db")
+			}
 			continue
 		}
 
 		if len(item.ToAddress) == 0 {
 			s.logger.Info().Msg("To address is empty, THORNode don't know where to send the fund , ignore")
+			if err := s.storage.ClearTxOutItem(key); err != nil {
+				s.logger.Error().Err(err).Msg("fail to mark it off from local db")
+			}
 			continue
 		}
 
@@ -319,16 +327,27 @@ func (s *Signer) signTxOutAndSendToChain(txOut types.TxOut) error {
 		if strings.EqualFold(out.Memo, thorchain.YggdrasilReturnMemo{}.GetType().String()) && item.Coin.IsEmpty() {
 			out, err = s.handleYggReturn(out)
 			if err != nil {
+				s.logger.Error().Err(err).Msg("failed to handle yggdrasil return")
+				if err := s.storage.ClearTxOutItem(key); err != nil {
+					s.logger.Error().Err(err).Msg("fail to mark it off from local db")
+				}
 				continue
 			}
 		}
 
 		err = s.signAndSendToChain(out, height)
 		if err != nil {
-			return fmt.Errorf("fail to broadcast tx to chain: %w", err)
+			// since we failed the txn, we'll clear the local db of this record
+			// for retry later
+			if err := s.storage.ClearTxOutItem(key); err != nil {
+				s.logger.Error().Err(err).Msg("fail to mark it off from local db")
+			}
+			s.logger.Error().Err(err).Msg("fail to broadcast tx to chain")
+			continue
 		}
-		if err := s.storage.SetTxOutItem(item, height); err != nil {
-			return fmt.Errorf("fail to mark it off from local db: %w", err)
+		if err := s.storage.SuccessTxOutItem(key); err != nil {
+			s.logger.Error().Err(err).Msg("fail to mark it off from local db")
+			continue
 		}
 	}
 
```

### bifrost/signer/thorchain_block_scanner_storage.go
```diff
@@ -3,6 +3,7 @@ package signer
 import (
 	"encoding/json"
 	"fmt"
+	"sync"
 
 	"github.com/pkg/errors"
 	"github.com/syndtr/goleveldb/leveldb"
@@ -16,7 +17,8 @@ const DefaultSignerLevelDBFolder = `signer_data`
 
 type ThorchainBlockScannerStorage struct {
 	*blockscanner.LevelDBScannerStorage
-	db *leveldb.DB
+	mutex *sync.RWMutex
+	db    *leveldb.DB
 }
 
 // NewThorchainBlockScannerStorage create a new instance of ThorchainBlockScannerStorage
@@ -30,10 +32,11 @@ func NewThorchainBlockScannerStorage(levelDbFolder string) (*ThorchainBlockScann
 	}
 	levelDbStorage, err := blockscanner.NewLevelDBScannerStorage(db)
 	if err != nil {
-		return nil, errors.New("fail to create leven db")
+		return nil, errors.New("fail to create level db")
 	}
 	return &ThorchainBlockScannerStorage{
 		LevelDBScannerStorage: levelDbStorage,
+		mutex:                 &sync.RWMutex{},
 		db:                    db,
 	}, nil
 }
@@ -102,12 +105,30 @@ func (s *ThorchainBlockScannerStorage) GetTxOutsForRetry(failedOnly bool) ([]typ
 	return results, nil
 }
 
-func (s *ThorchainBlockScannerStorage) SetTxOutItem(tai types.TxArrayItem, height int64) error {
-	return s.db.Put([]byte(tai.GetKey(height)), []byte{1}, nil)
+func (s *ThorchainBlockScannerStorage) SuccessTxOutItem(key string) error {
+	s.mutex.Lock()
+	defer s.mutex.Unlock()
+	return s.db.Put([]byte(key), []byte{0}, nil)
 }
 
-func (s *ThorchainBlockScannerStorage) HasTxOutItem(tai types.TxArrayItem, height int64) (bool, error) {
-	return s.db.Has([]byte(tai.GetKey(height)), nil)
+func (s *ThorchainBlockScannerStorage) ClearTxOutItem(key string) error {
+	s.mutex.Lock()
+	defer s.mutex.Unlock()
+	return s.db.Delete([]byte(key), nil)
+}
+
+func (s *ThorchainBlockScannerStorage) HasTxOutItem(key string) (bool, error) {
+	s.mutex.Lock()
+	defer s.mutex.Unlock()
+	ok, err := s.db.Has([]byte(key), nil)
+	if err != nil {
+		return false, err
+	}
+	if ok {
+		return true, nil
+	}
+	// mark as pending (2)
+	return false, s.db.Put([]byte(key), []byte{2}, nil)
 }
 
 // Close underlying db
```

### bifrost/thorclient/types/tx_out.go
```diff
@@ -52,5 +52,5 @@ type ChainsTxOut struct {
 
 // GetKey will return a key we can used it to save the infor to level db
 func (tai TxArrayItem) GetKey(height int64) string {
-	return fmt.Sprintf("%d-%s-%s-%s-%s", height, tai.VaultPubKey, tai.Memo, tai.Coin, tai.ToAddress)
+	return fmt.Sprintf("%d-%s-%s-%s-%s-%s", height, tai.InHash, tai.VaultPubKey, tai.Memo, tai.Coin, tai.ToAddress)
 }
```

# [?] Merge pull request #1438 from hyunsooda/sc-concurrency-crash-fix

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-07-07
Source: https://github.com/kaiachain/kaia/commit/70be58cd7b3da461efed2698597a997cce6263c5
Type: security-commit

## Details
Merge pull request #1438 from hyunsooda/sc-concurrency-crash-fix

[SC] Fixed concurrency API call bugs

## Patch
### console/jsre/deps/web3.js
```diff
@@ -3850,6 +3850,11 @@ var inputBlockNumberFormatter = function (blockNumber) {
     return utils.toHex(blockNumber);
 };
 
+var inputEmptyFormatter = function (a) {
+  if (a === undefined) return "";
+  else                 return a;
+}
+
 /**
  * Formats the input of a transaction and converts all values to HEX
  *
```

### console/web3ext/web3ext.go
```diff
@@ -1287,12 +1287,14 @@ web3._extend({
 		new web3._extend.Method({
 			name: 'subscribeBridge',
 			call: 'subbridge_subscribeBridge',
-			params: 2
+			params: 2,
+			inputFormatter: [null, web3._extend.formatters.inputEmptyFormatter]
 		}),
 		new web3._extend.Method({
 			name: 'unsubscribeBridge',
 			call: 'subbridge_unsubscribeBridge',
-			params: 2
+			params: 2,
+			inputFormatter: [null, web3._extend.formatters.inputEmptyFormatter]
 		}),
 		new web3._extend.Method({
 			name: 'KASAnchor',
@@ -1307,22 +1309,26 @@ web3._extend({
 		new web3._extend.Method({
 			name: 'registerBridge',
 			call: 'subbridge_registerBridge',
-			params: 2
+			params: 3,
+			inputFormatter: [null, null, web3._extend.formatters.inputEmptyFormatter]
 		}),
 		new web3._extend.Method({
 			name: 'deregisterBridge',
 			call: 'subbridge_deregisterBridge',
-			params: 2
+			params: 2,
+			inputFormatter: [null, web3._extend.formatters.inputEmptyFormatter]
 		}),
 		new web3._extend.Method({
 			name: 'registerToken',
 			call: 'subbridge_registerToken',
-			params: 4
+			params: 4,
+			inputFormatter: [null, null, null, web3._extend.formatters.inputEmptyFormatter]
 		}),
 		new web3._extend.Method({
 			name: 'deregisterToken',
 			call: 'subbridge_deregisterToken',
-			params: 4
+			params: 4,
+			inputFormatter: [null, null, null, web3._extend.formatters.inputEmptyFormatter]
 		}),
 		new web3._extend.Method({
 			name: 'convertRequestTxHashToHandleTxHash',
@@ -1397,6 +1403,16 @@ web3._extend({
 			call: 'subbridge_setChildOperatorFeePayer',
 			params: 1
 		}),
+		new web3._extend.Method({
+			name: 'getBridgePairByAlias',
+			call: 'subbridge_getBridgePairByAlias',
+			params: 1
+		}),
+		new web3._extend.Method({
+			name: 'changeBridgeAlias',
+			call: 'subbridge_changeBridgeAlias',
+			params: 2
+		}),
 		new web3._extend.Method({
 			name: 'setParentBridgeOperatorGasLimit',
 			call: 'subbridge_setParentBridgeOperatorGasLimit',
```

### node/sc/api_bridge.go
```diff
@@ -20,6 +20,7 @@ import (
 	"context"
 	"fmt"
 	"math/big"
+	"strings"
 
 	"github.com/klaytn/klaytn/blockchain/types"
 	"github.com/klaytn/klaytn/common"
@@ -35,6 +36,27 @@ var (
 	ErrBridgeContractVersionMismatch = errors.New("Bridge contract version mismatch")
 )
 
+func parseBridgeAddrWithAlias(sb *SubBridge, cBridgeAddrOrAlias, pBridgeAddrOrFirstParam string, args ...interface{}) (common.Address, common.Address, []interface{}, error) {
+	if !strings.HasPrefix(cBridgeAddrOrAlias, "0x") {
+		// Takes pBridgeAddr as the first API argument and append residual arguments.
+		var newArgs []interface{}
+		if len(args) > 0 {
+			newArgs = append([]interface{}{pBridgeAddrOrFirstParam}, args[:len(args)-1]...)
+		}
+		cBridgeAddr, pBridgeAddr, err := sb.bridgeManager.getAddrByAlias(cBridgeAddrOrAlias)
+		return cBridgeAddr, pBridgeAddr, newArgs, err
+	} else {
+		return common.HexToAddress(cBridgeAddrOrAlias), common.HexToAddress(pBridgeAddrOrFirstParam), args, nil
+	}
+}
+
+func stringDeref(str *string) string {
+	if str == nil {
+		return ""
+	}
+	return *str
+}
+
 // MainBridgeAPI Implementation for main-bridge node
 type MainBridgeAPI struct {
 	mainBridge *MainBridge
@@ -138,16 +160,16 @@ func (sb *SubBridgeAPI) DeployBridge() ([]common.Address, error) {
 		return nil, err
 	}
 
-	err = sb.subBridge.bridgeManager.SetJournal(cBridgeAddr, pBridgeAddr)
+	err = sb.subBridge.bridgeManager.SetJournal("", cBridgeAddr, pBridgeAddr)
 	if err != nil {
 		return nil, err
 	}
 
 	return []common.Address{cBridgeAddr, pBridgeAddr}, nil
 }
 
-// SubscribeBridge enables the given child/parent chain bridges to subscribe the events.
-func (sb *SubBridgeAPI) SubscribeBridge(cBridgeAddr, pBridgeAddr common.Address) error {
+// doSubscribeBridge enables the given child/parent chain bridges to subscribe the events.
+func (sb *SubBridgeAPI) doSubscribeBridge(cBridgeAddr, pBridgeAddr common.Address) error {
 	if !sb.subBridge.bridgeManager.IsValidBridgePair(cBridgeAddr, pBridgeAddr) {
 		return ErrInvalidBridgePair
 	}
@@ -165,7 +187,9 @@ func (sb *SubBridgeAPI) SubscribeBridge(cBridgeAddr, pBridgeAddr common.Address)
 		return err
 	}
 
+	sb.subBridge.bridgeManager.journal.cacheMu.Lock()
 	sb.subBridge.bridgeManager.journal.cache[cBridgeAddr].Subscribed = true
+	sb.subBridge.bridgeManager.journal.cacheMu.Unlock()
 
 	// Update the journal's subscribed flag.
 	sb.subBridge.bridgeManager.journal.rotate(sb.subBridge.bridgeManager.GetAllBridge())
@@ -179,21 +203,41 @@ func (sb *SubBridgeAPI) SubscribeBridge(cBridgeAddr, pBridgeAddr common.Address)
 	return nil
 }
 
-// UnsubscribeBridge disables the event subscription of the given child/parent chain bridges.
-func (sb *SubBridgeAPI) UnsubscribeBridge(cBridgeAddr, pBridgeAddr common.Address) error {
+func (sb *SubBridgeAPI) SubscribeBridge(cBridgeAddrOrAlias, pBridgeAddrOrEmpty *string) error {
+	cBridgeAddrOrAliasStr, pBridgeAddrOrEmptyStr := stringDeref(cBridgeAddrOrAlias), stringDeref(pBridgeAddrOrEmpty)
+	cBridgeAddr, pBridgeAddr, _, err := parseBridgeAddrWithAlias(sb.subBridge, cBridgeAddrOrAliasStr, pBridgeAddrOrEmptyStr)
+	if err != nil {
+		return err
+	}
+	return sb.doSubscribeBridge(cBridgeAddr, pBridgeAddr)
+}
+
+// doUnsubscribeBridge disables the event subscription of the given child/parent chain bridges.
+func (sb *SubBridgeAPI) doUnsubscribeBridge(cBridgeAddr, pBridgeAddr common.Address) error {
 	if !sb.subBridge.bridgeManager.IsValidBridgePair(cBridgeAddr, pBridgeAddr) {
 		return ErrInvalidBridgePair
 	}
 
 	sb.subBridge.bridgeManager.UnsubscribeEvent(cBridgeAddr)
 	sb.subBridge.bridgeManager.UnsubscribeEvent(pBridgeAddr)
 
+	sb.subBridge.bridgeManager.journal.cacheMu.Lock()
 	sb.subBridge.bridgeManager.journal.cache[cBridgeAddr].Subscribed = false
+	sb.subBridge.bridgeManager.journal.cacheMu.Unlock()
 
 	sb.subBridge.bridgeManager.journal.rotate(sb.subBridge.bridgeManager.GetAllBridge())
 	return nil
 }
 
+func (sb *SubBridgeAPI) UnsubscribeBridge(cBridgeAddrOrAlias, pBridgeAddrOrEmpty *string) error {
+	cBridgeAddrOrAliasStr, pBridgeAddrOrEmptyStr := stringDeref(cBridgeAddrOrAlias), stringDeref(pBridgeAddrOrEmpty)
+	cBridgeAddr, pBridgeAddr, _, err := parseBridgeAddrWithAlias(sb.subBridge, cBridgeAddrOrAliasStr, pBridgeAddrOrEmptyStr)
+	if err != nil {
+		return err
+	}
+	return sb.doUnsubscribeBridge(cBridgeAddr, pBridgeAddr)
+}
+
 func (sb *SubBridgeAPI) ConvertRequestTxHashToHandleTxHash(hash common.Hash) common.Hash {
 	return sb.subBridge.chainDB.ReadHandleTxHashFromRequestTxHash(hash)
 }
@@ -210,6 +254,18 @@ func (sb *SubBridgeAPI) ListBridge() []*BridgeJournal {
 	return sb.subBridge.bridgeManager.GetAllBridge()
 }
 
+func (sb *SubBridgeAPI) GetBridgePairByAlias(bridgeAlias string) *BridgeJournal {
+	return sb.subBridge.bridgeManager.GetBridge(bridgeAlias)
+}
+
+func (sb *SubBridgeAPI) ChangeBridgeAlias(oldAlias, newAlias string) error {
+	bm := sb.subBridge.bridgeManager
+	if err := bm.journal.ChangeBridgeAlias(oldAlias, newAlias); err != nil {
+		return err
+	}
+	return bm.journal.rotate(bm.GetAllBridge())
+}
+
 func (sb *SubBridgeAPI) GetBridgeInformation(bridgeAddr common.Address) (map[string]interface{}, error) {
 	if ctBridge := sb.subBridge.bridgeManager.GetCounterPartBridgeAddr(bridgeAddr); ctBridge == (common.Address{}) {
 		return nil, ErrInvalidBridgePair
@@ -254,7 +310,7 @@ func (sb *SubBridgeAPI) GetAnchoring() bool {
 	return sb.subBridge.GetAnchoringTx()
 }
 
-func (sb *SubBridgeAPI) RegisterBridge(cBridgeAddr common.Address, pBridgeAddr common.Address) error {
+func (sb *SubBridgeAPI) doRegisterBridge(cBridgeAddr common.Address, pBridgeAddr common.Address) error {
 	cBridge, err := bridge.NewBridge(cBridgeAddr, sb.subBridge.localBackend)
 	if err != nil {
 		return err
@@ -274,21 +330,24 @@ func (sb *SubBridgeAPI) RegisterBridge(cBridgeAddr common.Address, pBridgeAddr c
 		bm.DeleteBridgeInfo(cBridgeAddr)
 		return err
 	}
+	return nil
+}
 
-	err = bm.SetJournal(cBridgeAddr, pBridgeAddr)
-	if err != nil {
+func (sb *SubBridgeAPI) RegisterBridge(cBridgeAddr, pBridgeAddr common.Address, bridgeAliasP *string) error {
+	bridgeAlias := stringDeref(bridgeAliasP)
+	if err := sb.subBridge.bridgeManager.SetJournal(bridgeAlias, cBridgeAddr, pBridgeAddr); err != nil {
 		return err
 	}
-
-	return nil
+	return sb.doRegisterBridge(cBridgeAddr, pBridgeAddr)
 }
 
-func (sb *SubBridgeAPI) DeregisterBridge(cBridgeAddr common.Address, pBridgeAddr common.Address) error {
+func (sb *SubBridgeAPI) doDeregisterBridge(cBridgeAddr common.Address, pBridgeAddr common.Address) error {
 	if !sb.subBridge.bridgeManager.IsValidBridgePair(cBridgeAddr, pBridgeAddr) {
 		return ErrInvalidBridgePair
 	}
 
 	bm := sb.subBridge.bridgeManager
+	bm.journal.cacheMu.Lock()
 	journal := bm.journal.cache[cBridgeAddr]
 
 	if journal.Subscribed {
@@ -299,6 +358,7 @@ func (sb *SubBridgeAPI) DeregisterBridge(cBridgeAddr common.Address, pBridgeAddr
 	}
 
 	delete(bm.journal.cache, cBridgeAddr)
+	bm.journal.cacheMu.Unlock()
 
 	if err := bm.journal.rotate(bm.GetAllBridge()); err != nil {
 		logger.Warn("failed to rotate bridge journal", "err", err, "cBridge", cBridgeAddr.String(), "pBridge", pBridgeAddr.String())
@@ -311,11 +371,22 @@ func (sb *SubBridgeAPI) DeregisterBridge(cBridgeAddr common.Address, pBridgeAddr
 	if err := bm.DeleteBridgeInfo(pBridgeAddr); err != nil {
 		logger.Warn("failed to Delete parent chain bridge info", "err", err, "bridge", pBridgeAddr.String())
 	}
-
 	return nil
 }
 
-func (sb *SubBridgeAPI) RegisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTokenAddr common.Address) error {
+func (sb *SubBridgeAPI) DeregisterBridge(cBridgeAddrOrAlias, pBridgeAddrOrEmpty *string) error {
+	cBridgeAddrOrAliasStr, pBridgeAddrOrEmptyStr := stringDeref(cBridgeAddrOrAlias), stringDeref(pBridgeAddrOrEmpty)
+	cBridgeAddr, pBridgeAddr, _, err := parseBridgeAddrWithAlias(sb.subBridge, cBridgeAddrOrAliasStr, pBridgeAddrOrEmptyStr)
+	if err != nil {
+		return err
+	}
+	sb.subBridge.bridgeManager.journal.cacheMu.Lock()
+	delete(sb.subBridge.bridgeManager.journal.aliasCache, cBridgeAddrOrAliasStr)
+	sb.subBridge.bridgeManager.journal.cacheMu.Unlock()
+	return sb.doDeregisterBridge(cBridgeAddr, pBridgeAddr)
+}
+
+func (sb *SubBridgeAPI) doRegisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTokenAddr common.Address) error {
 	if !sb.subBridge.bridgeManager.IsValidBridgePair(cBridgeAddr, pBridgeAddr) {
 		return ErrInvalidBridgePair
 	}
@@ -340,6 +411,7 @@ func (sb *SubBridgeAPI) RegisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTok
 	cBi.account.Lock()
 	tx, err := cBi.bridge.RegisterToken(cBi.account.GenerateTransactOpts(), cTokenAddr, pTokenAddr)
 	if err != nil {
+		cBi.DeregisterToken(cTokenAddr, pTokenAddr)
 		cBi.account.UnLock()
 		return err
 	}
@@ -350,6 +422,7 @@ func (sb *SubBridgeAPI) RegisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTok
 	pBi.account.Lock()
 	tx, err = pBi.bridge.RegisterToken(pBi.account.GenerateTransactOpts(), pTokenAddr, cTokenAddr)
 	if err != nil {
+		pBi.DeregisterToken(pTokenAddr, cTokenAddr)
 		pBi.account.UnLock()
 		return err
 	}
@@ -361,6 +434,16 @@ func (sb *SubBridgeAPI) RegisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTok
 	return nil
 }
 
+func (sb *SubBridgeAPI) RegisterToken(cBridgeAddrOrAlias, pBridgeOrChildToken, cTokenAddrOrPtokenAddr, pTokenAddrOrEmpty *string) error {
+	cBridgeAddrOrAliasStr, pBridgeAddrOrChildTokenStr, cTokenAddrOrPtokenAddrStr, pTokenAddrOrEmptyStr := stringDeref(cBridgeAddrOrAlias), stringDeref(pBridgeOrChildToken), stringDeref(cTokenAddrOrPtokenAddr), stringDeref(pTokenAddrOrEmpty)
+	cBridgeAddr, pBridgeAddr, args, err := parseBridgeAddrWithAlias(sb.subBridge, cBridgeAddrOrAliasStr, pBridgeAddrOrChildTokenStr, cTokenAddrOrPtokenAddrStr, pTokenAddrOrEmptyStr)
+	if err != nil {
+		return err
+	}
+	cTokenAddr, pTokenAddr := common.HexToAddress(args[0].(string)), common.HexToAddress(args[1].(string))
+	return sb.doRegisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTokenAddr)
+}
+
 func (sb *SubBridgeAPI) GetParentTransactionReceipt(txHash common.Hash) (map[string]interface{}, error) {
 	ctx := context.Background()
 	return sb.subBridge.remoteBackend.(RemoteBackendInterface).TransactionReceiptRpcOutput(ctx, txHash)
@@ -390,7 +473,11 @@ func (sb *SubBridgeAPI) GetFeeReceiver(bridgeAddr common.Address) (common.Addres
 	return sb.subBridge.bridgeManager.GetFeeReceiver(bridgeAddr)
 }
 
-func (sb *SubBridgeAPI) DeregisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTokenAddr common.Address) error {
+func (sb *SubBridgeAPI) doDeregisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTokenAddr common.Address) error {
+	if !sb.subBridge.bridgeManager.IsValidBridgePair(cBridgeAddr, pBridgeAddr) {
+		return ErrInvalidBridgePair
+	}
+
 	cBi, cExist := sb.subBridge.bridgeManager.GetBridgeInfo(cBridgeAddr)
 	pBi, pExist := sb.subBridge.bridgeManager.GetBridgeInfo(pBridgeAddr)
 
@@ -428,6 +515,16 @@ func (sb *SubBridgeAPI) DeregisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pT
 	return err
 }
 
+func (sb *SubBridgeAPI) DeregisterToken(cBridgeAddrOrAlias, pBridgeOrChildToken, cTokenAddrOrPtokenAddr, pTokenAddrOrEmpty *string) error {
+	cBridgeAddrOrAliasStr, pBridgeAddrOrChildTokenStr, cTokenAddrOrPtokenAddrStr, pTokenAddrOrEmptyStr := stringDeref(cBridgeAddrOrAlias), stringDeref(pBridgeOrChildToken), stringDeref(cTokenAddrOrPtokenAddr), stringDeref(pTokenAddrOrEmpty)
+	cBridgeAddr, pBridgeAddr, args, err := parseBridgeAddrWithAlias(sb.subBridge, cBridgeAddrOrAliasStr, pBridgeAddrOrChildTokenStr, cTokenAddrOrPtokenAddrStr, pTokenAddrOrEmptyStr)
+	if err != nil {
+		return err
+	}
+	cTokenAddr, pTokenAddr := common.HexToAddress(args[0].(string)), common.HexToAddress(args[1].(string))
+	return sb.doDeregisterToken(cBridgeAddr, pBridgeAddr, cTokenAddr, pTokenAddr)
+}
+
 // AddPeer requests connecting to a remote node, and also maintaining the new
 // connection at all times, even reconnecting if it is lost.
 func (sb *SubBridgeAPI) AddPeer(url string) (bool, error) {
```

### node/sc/bridge_addr_journal.go
```diff
@@ -24,37 +24,51 @@ import (
 	"errors"
 	"io"
 	"os"
+	"strings"
+	"sync"
 
 	"github.com/klaytn/klaytn/common"
 	"github.com/klaytn/klaytn/node/sc/bridgepool"
 	"github.com/klaytn/klaytn/rlp"
 )
 
 var (
-	errNoActiveAddressJournal = errors.New("no active address journal")
-	errDuplicatedJournal      = errors.New("duplicated journal is inserted")
-	errEmptyBridgeAddress     = errors.New("empty bridge address is not allowed")
+	ErrNoActiveAddressJournal = errors.New("no active address journal")
+	ErrDuplicatedJournal      = errors.New("duplicated journal is inserted")
+	ErrDuplicatedAlias        = errors.New("duplicated alias")
+	ErrEmptyBridgeAddress     = errors.New("empty bridge address is not allowed")
+	ErrEmptyJournalCache      = errors.New("empty bridge journal")
+	ErrEmptyBridgeAlias       = errors.New("empty bridge Alias")
+	ErrNotAllowedAliasFormat  = errors.New("Not allowed bridge alias format")
 )
 
 // bridgeAddrJournal is a rotating log of addresses with the aim of storing locally
 // created addresses to allow deployed bridge contracts to survive node restarts.
 type bridgeAddrJournal struct {
-	path   string         // Filesystem path to store the addresses at
-	writer io.WriteCloser // Output stream to write new addresses into
-	cache  map[common.Address]*BridgeJournal
+	path       string         // Filesystem path to store the addresses at
+	writer     io.WriteCloser // Output stream to write new addresses into
+	cache      map[common.Address]*BridgeJournal
+	aliasCache map[string]common.Address
+	writerMu   *sync.Mutex
+	cacheMu    *sync.RWMutex
 }
 
 // newBridgeAddrJournal creates a new bridge addr journal to
 func newBridgeAddrJournal(path string) *bridgeAddrJournal {
 	return &bridgeAddrJournal{
-		path:  path,
-		cache: make(map[common.Address]*BridgeJournal),
+		path:       path,
+		cache:      make(map[common.Address]*BridgeJournal),
+		aliasCache: make(map[string]common.Address),
+		writerMu:   &sync.Mutex{},
+		cacheMu:    &sync.RWMutex{},
 	}
 }
 
 // load parses a address journal dump from disk, loading its contents into
 // the specified pool.
 func (journal *bridgeAddrJournal) load(add func(journal BridgeJournal) error) error {
+	journal.writerMu.Lock()
+	defer journal.writerMu.Unlock()
 	// Skip the parsing if the journal file doens't exist at all
 	if _, err := os.Stat(journal.path); os.IsNotExist(err) {
 		return nil
@@ -74,15 +88,33 @@ func (journal *bridgeAddrJournal) load(add func(journal BridgeJournal) error) er
 	stream := rlp.NewStream(input, 0)
 	total, dropped := 0, 0
 
-	var failure error
+	var (
+		failure              error
+		aliasBridgeDecodeErr = false
+	)
 	for {
 		// Parse the next address and terminate on error
 		addr := new(BridgeJournal)
+		if aliasBridgeDecodeErr {
+			addr.isLegacyBridgeJournal = true
+		}
 		if err = stream.Decode(addr); err != nil {
-			if err != io.EOF {
+			if err == io.EOF {
+				break
+			} else if err == ErrBridgeAliasFormatDecode {
+				input.Close()
+				input, err = os.Open(journal.path)
+				if err != nil {
+					failure = err
+					break
+				}
+				aliasBridgeDecodeErr = true
+				stream.Reset(input, 0)
+				continue
+			} else {
 				failure = err
+				break
 			}
-			break
 		}
 
 		total++
@@ -97,34 +129,71 @@ func (journal *bridgeAddrJournal) load(add func(journal BridgeJournal) error) er
 	return failure
 }
 
+// ChangeBridgeAlias changes oldBridgeAlias to newBridgeAlias
+func (journal *bridgeAddrJournal) ChangeBridgeAlias(oldBridgeAlias, newBridgeAlias string) error {
+	journal.cacheMu.Lock()
+	defer journal.cacheMu.Unlock()
+	if addr, ok := journal.aliasCache[oldBridgeAlias]; ok {
+		delete(journal.aliasCache, oldBridgeAlias)
+		journal.aliasCache[newBridgeAlias] = addr
+		journal.cache[addr].BridgeAlias = newBridgeAlias
+		return nil
+	}
+	return ErrEmptyBridgeAlias
+}
+
 // insert adds the specified address to the local disk journal.
-func (journal *bridgeAddrJournal) insert(localAddress common.Address, remoteAddress common.Address) error {
+func (journal *bridgeAddrJournal) insert(bridgeAlias string, localAddress common.Address, remoteAddress common.Address) error {
+	// lock order is important
+	journal.cacheMu.Lock()
+	journal.writerMu.Lock()
+
+	defer func() {
+		journal.cacheMu.Unlock()
+		journal.writerMu.Unlock()
+	}()
+
+	if strings.HasPrefix(bridgeAlias, "0x") {
+		return ErrNotAllowedAliasFormat
+	}
+	if len(bridgeAlias) != 0 && journal.aliasCache[bridgeAlias] != (common.Address{}) {
+		return ErrDuplicatedAlias
+	}
+
 	if journal.cache[localAddress] != nil {
-		return errDuplicatedJournal
+		return ErrDuplicatedJournal
 	}
 	if journal.writer == nil {
-		return errNoActiveAddressJournal
+		return ErrNoActiveAddressJournal
 	}
 	empty := common.Address{}
 	if localAddress == empty || remoteAddress == empty {
-		return errEmptyBridgeAddress
+		return ErrEmptyBridgeAddress
 	}
 	// TODO-Klaytn-ServiceChain: support false paired
 	item := BridgeJournal{
+		bridgeAlias,
 		localAddress,
 		remoteAddress,
 		false,
+		false,
 	}
 	if err := rlp.Encode(journal.writer, &item); err != nil {
 		return err
 	}
+
 	journal.cache[localAddress] = &item
+	if len(bridgeAlias) != 0 {
+		journal.aliasCache[bridgeAlias] = localAddress
+	}
 	return nil
 }
 
 // rotate regenerates the addresses journal based on the current contents of
 // the address pool.
 func (journal *bridgeAddrJournal) rotate(all []*BridgeJournal) error {
+	journal.writerMu.Lock()
+	defer journal.writerMu.Unlock()
 	// Close the current journal (if any is open)
 	if journal.writer != nil {
 		if err := journal.writer.Close(); err != nil {
@@ -163,8 +232,10 @@ func (journal *bridgeAddrJournal) rotate(all []*BridgeJournal) error {
 
 // close flushes the addresses journal contents to disk and closes the file.
 func (journal *bridgeAddrJournal) close() error {
-	var err error
+	journal.writerMu.Lock()
+	defer journal.writerMu.Unlock()
 
+	var err error
 	if journal.writer != nil {
 		err = journal.writer.Close()
 		journal.writer = nil
```

### node/sc/bridge_addr_journal_test.go
```diff
@@ -45,15 +45,15 @@ func TestBridgeJournal(t *testing.T) {
 		t.Fatalf("fail to rotate journal %v", err)
 	}
 
-	err := journal.insert(common.BytesToAddress([]byte("test1")), common.BytesToAddress([]byte("test2")))
+	err := journal.insert("", common.BytesToAddress([]byte("test1")), common.BytesToAddress([]byte("test2")))
 	if err != nil {
 		t.Fatalf("fail to insert address %v", err)
 	}
-	err = journal.insert(common.BytesToAddress([]byte("test2")), common.BytesToAddress([]byte("test3")))
+	err = journal.insert("", common.BytesToAddress([]byte("test2")), common.BytesToAddress([]byte("test3")))
 	if err != nil {
 		t.Fatalf("fail to insert address %v", err)
 	}
-	err = journal.insert(common.BytesToAddress([]byte("test3")), common.BytesToAddress([]byte("test1")))
+	err = journal.insert("", common.BytesToAddress([]byte("test3")), common.BytesToAddress([]byte("test1")))
 	if err != nil {
 		t.Fatalf("fail to insert address %v", err)
 	}
@@ -108,7 +108,7 @@ func TestBridgeJournalCache(t *testing.T) {
 	localAddr := common.BytesToAddress([]byte("test1"))
 	remoteAddr := common.BytesToAddress([]byte("test2"))
 
-	err := journals.insert(localAddr, remoteAddr)
+	err := journals.insert("", localAddr, remoteAddr)
 	if err != nil {
 		t.Fatalf("fail to insert address %v", err)
 	}
```

### node/sc/bridge_manager.go
```diff
@@ -55,13 +55,14 @@ const (
 )
 
 var (
-	ErrInvalidTokenPair     = errors.New("invalid token pair")
-	ErrNoBridgeInfo         = errors.New("bridge information does not exist")
-	ErrDuplicatedBridgeInfo = errors.New("bridge information is duplicated")
-	ErrDuplicatedToken      = errors.New("token is duplicated")
-	ErrNoRecovery           = errors.New("recovery does not exist")
-	ErrAlreadySubscribed    = errors.New("already subscribed")
-	ErrBridgeRestore        = errors.New("restoring bridges is failed")
+	ErrInvalidTokenPair        = errors.New("invalid token pair")
+	ErrNoBridgeInfo            = errors.New("bridge information does not exist")
+	ErrDuplicatedBridgeInfo    = errors.New("bridge information is duplicated")
+	ErrDuplicatedToken         = errors.New("token is duplicated")
+	ErrNoRecovery              = errors.New("recovery does not exist")
+	ErrAlreadySubscribed       = errors.New("already subscribed")
+	ErrBridgeRestore           = errors.New("restoring bridges is failed")
+	ErrBridgeAliasFormatDecode = errors.New("failed to decode alias-format bridge")
 )
 
 var handleVTmethods = map[uint8]string{
@@ -76,9 +77,11 @@ type HandleValueTransferEvent struct {
 }
 
 type BridgeJournal struct {
-	ChildAddress  common.Address `json:"childAddress"`
-	ParentAddress common.Address `json:"parentAddress"`
-	Subscribed    bool           `json:"subscribed"`
+	BridgeAlias           string         `json:"bridgeAlias"`
+	ChildAddress          common.Address `json:"childAddress"`
+	ParentAddress         common.Address `json:"parentAddress"`
+	Subscribed            bool           `json:"subscribed"`
+	isLegacyBridgeJournal bool
 }
 
 type BridgeInfo struct {
@@ -95,6 +98,7 @@ type BridgeInfo struct {
 	subscribed         bool
 
 	counterpartToken map[common.Address]common.Address
+	ctTokenMu        sync.RWMutex
 
 	pendingRequestEvent *bridgepool.ItemSortedMap
 
@@ -120,26 +124,26 @@ func (ev requestEvent) Nonce() uint64 {
 
 func NewBridgeInfo(sb *SubBridge, addr common.Address, bridge *bridgecontract.Bridge, cpAddr common.Address, cpBridge *bridgecontract.Bridge, account *accountInfo, local, subscribed bool, cpBackend Backend) (*BridgeInfo, error) {
 	bi := &BridgeInfo{
-		sb,
-		sb.chainDB,
-		cpBackend,
-		addr,
-		cpAddr,
-		account,
-		bridge,
-		cpBridge,
-		local,
-		subscribed,
-		make(map[common.Address]common.Address),
-		bridgepool.NewItemSortedMap(bridgepool.UnlimitedItemSortedMap),
-		true,
-		0,
-		0,
-		0,
-		0,
-		make(chan struct{}),
-		make(chan struct{}),
-		bridgepool.NewItemSortedMap(maxHandledEventSize),
+		subBridge:                   sb,
+		bridgeDB:                    sb.chainDB,
+		counterpartBackend:          cpBackend,
+		address:                     addr,
+		counterpartAddress:          cpAddr,
+		account:                     account,
+		bridge:                      bridge,
+		counterpartBridge:           cpBridge,
+		onChildChain:                local,
+		subscribed:                  subscribed,
+		counterpartToken:            make(map[common.Address]common.Address),
+		pendingRequestEvent:         bridgepool.NewItemSortedMap(bridgepool.UnlimitedItemSortedMap),
+		isRunning:                   true,
+		handleNonce:                 0,
+		lowerHandleNonce:            0,
+		requestNonceFromCounterPart: 0,
+		requestNonce:                0,
+		newEvent:                    make(chan struct{}),
+		closed:                      make(chan struct{}),
+		handledEvent:                bridgepool.NewItemSortedMap(maxHandledEventSize),
 	}
 
 	if err := bi.UpdateInfo(); err != nil {
@@ -186,6 +190,9 @@ func (bi *BridgeInfo) loop() {
 }
 
 func (bi *BridgeInfo) RegisterToken(token, counterpartToken common.Address) error {
+	bi.ctTokenMu.Lock()
+	defer bi.ctTokenMu.Unlock()
+
 	_, exist := bi.counterpartToken[token]
 	if exist {
 		return ErrDuplicatedToken
@@ -195,6 +202,9 @@ func (bi *BridgeInfo) RegisterToken(token, counterpartToken common.Address) erro
 }
 
 func (bi *BridgeInfo) DeregisterToken(token, counterpartToken common.Address) error {
+	bi.ctTokenMu.Lock()
+	defer bi.ctTokenMu.Unlock()
+
 	_, exist := bi.counterpartToken[token]
 	if !exist {
 		return ErrInvalidTokenPair
@@ -204,6 +214,9 @@ func (bi *BridgeInfo) DeregisterToken(token, counterpartToken common.Address) er
 }
 
 func (bi *BridgeInfo) GetCounterPartToken(token common.Address) common.Address {
+	bi.ctTokenMu.RLock()
+	defer bi.ctTokenMu.RUnlock()
+
 	cpToken, exist := bi.counterpartToken[token]
 	if !exist {
 		return common.Address{}
@@ -426,21 +439,40 @@ func (bi *BridgeInfo) GetCurrentBlockNumber() (uint64, error) {
 
 // DecodeRLP decodes the Klaytn
 func (b *BridgeJournal) DecodeRLP(s *rlp.Stream) error {
-	var elem struct {
+	var LegacyBridgeAddrInfo struct {
 		LocalAddress  common.Address
 		RemoteAddress common.Address
 		Paired        bool
 	}
-	if err := s.Decode(&elem); err != nil {
-		return err
+	var BridgeAddrInfo struct {
+		BridgeAlias   string
+		LocalAddress  common.Address
+		RemoteAddress common.Address
+		Paired        bool
+	}
+	if !b.isLegacyBridgeJournal {
+		if err := s.Decode(&BridgeAddrInfo); err != nil {
+			logger.Trace("Failed to decode. Try decode again with legacy structure")
+			b.isLegacyBridgeJournal = true
+			if err == io.EOF {
+				return err
+			}
+			return ErrBridgeAliasFormatDecode
+		}
+		b.BridgeAlias, b.ChildAddress, b.ParentAddress, b.Subscribed = BridgeAddrInfo.BridgeAlias, BridgeAddrInfo.LocalAddress, BridgeAddrInfo.RemoteAddress, BridgeAddrInfo.Paired
+	} else {
+		if err := s.Decode(&LegacyBridgeAddrInfo); err != nil {
+			return err
+		}
+		b.BridgeAlias, b.ChildAddress, b.ParentAddress, b.Subscribed = "", LegacyBridgeAddrInfo.LocalAddress, LegacyBridgeAddrInfo.RemoteAddress, LegacyBridgeAddrInfo.Paired
 	}
-	b.ChildAddress, b.ParentAddress, b.Subscribed = elem.LocalAddress, elem.RemoteAddress, elem.Paired
 	return nil
 }
 
 // EncodeRLP serializes a BridgeJournal into the Klaytn RLP BridgeJournal format.
 func (b *BridgeJournal) EncodeRLP(w io.Writer) error {
 	return rlp.Encode(w, []interface{}{
+		b.BridgeAlias,
 		b.ChildAddress,
 		b.ParentAddress,
 		b.Subscribed,
@@ -455,7 +487,8 @@ type BridgeManager struct {
 	receivedEvents map[common.Address][]event.Subscription
 	withdrawEvents map[common.Address]event.Subscription
 	bridges        map[common.Address]*BridgeInfo
-	mu             sync.RWMutex
+	bridgesMu      sync.RWMutex
+	tokenEventMu   sync.RWMutex
 
 	reqVTevFeeder        event.Feed
 	reqVTevEncodedFeeder event.Feed
@@ -481,17 +514,25 @@ func NewBridgeManager(main *SubBridge) (*BridgeManager, error) {
 	}
 
 	logger.Info("Load Bridge Address from JournalFiles ", "path", bridgeManager.journal.path)
+	bridgeManager.journal.cacheMu.Lock()
+
 	bridgeManager.journal.cache = make(map[common.Address]*BridgeJournal)
+	bridgeManager.journal.aliasCache = make(map[string]common.Address)
 
 	if err := bridgeManager.journal.load(func(gwjournal BridgeJournal) error {
 		logger.Info("Load Bridge Address from JournalFiles ",
-			"local address", gwjournal.ChildAddress.Hex(), "remote address", gwjournal.ParentAddress.Hex())
+			"alias", gwjournal.BridgeAlias,
+			"local address", gwjournal.ChildAddress.Hex(),
+			"remote address", gwjournal.ParentAddress.Hex())
 		bridgeManager.journal.cache[gwjournal.ChildAddress] = &gwjournal
+		bridgeManager.journal.aliasCache[gwjournal.BridgeAlias] = gwjournal.ChildAddress
 		return nil
 	}); err != nil {
 		logger.Error("fail to load bridge address", "err", err)
 	}
 
+	bridgeManager.journal.cacheMu.Unlock()
+
 	if err := bridgeManager.journal.rotate(bridgeManager.GetAllBridge()); err != nil {
 		logger.Error("fail to rotate bridge journal", "err", err)
 	}
@@ -502,14 +543,10 @@ func NewBridgeManager(main *SubBridge) (*BridgeManager, error) {
 func (bm *BridgeManager) IsValidBridgePair(bridge1, bridge2 common.Address) bool {
 	b1, ok1 := bm.GetBridgeInfo(bridge1)
 	b2, ok2 := bm.GetBridgeInfo(bridge2)
-
-	if ok1 && ok2 {
-		if bridge1 == b2.counterpartAddress && bridge2 == b1.counterpartAddress {
-			return true
-		}
+	if !ok1 || !ok2 {
+		return false
 	}
-
-	return false
+	return bridge1 == b2.counterpartAddress && bridge2 == b1.counterpartAddress
 }
 
 func (bm *BridgeManager) GetCounterPartBridgeAddr(bridgeAddr common.Address) common.Address {
@@ -530,8 +567,8 @@ func (bm *BridgeManager) GetCounterPartBridge(bridgeAddr common.Address) *bridge
 
 // LogBridgeStatus logs the bridge contract requested/handled nonce status as an information.
 func (bm *BridgeManager) LogBridgeStatus() {
-	bm.mu.RLock()
-	defer bm.mu.RUnlock()
+	bm.bridgesMu.RLock()
+	defer bm.bridgesMu.RUnlock()
 
 	if len(bm.bridges) == 0 {
 		return
@@ -579,29 +616,55 @@ func (bm *BridgeManager) SubscribeHandleVTev(ch chan<- *HandleValueTransferEvent
 	return bm.scope.Track(bm.handleEventFeeder.Subscribe(ch))
 }
 
+// getAddrByAlias returns a pair of child bridge address and parent bridge address
+func (bm *BridgeManager) getAddrByAlias(bridgeAlias string) (common.Address, common.Address, error) {
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
+
+	journalAddr, ok := bm.journal.aliasCache[bridgeAlias]
+	if !ok {
+		return common.Address{}, common.Address{}, ErrEmptyBridgeAlias
+	}
+	journal, ok := bm.journal.cache[journalAddr]
+	if !ok {
+		return common.Address{}, common.Address{}, ErrEmptyJournalCache
+	}
+	return journal.ChildAddress, journal.ParentAddress, nil
+}
+
+// GetBridge returns bridge journal structure that contains local(child) and remote(parent) addresses.
+func (bm *BridgeManager) GetBridge(bridgeAlias string) *BridgeJournal {
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
+
+	return bm.journal.cache[bm.journal.aliasCache[bridgeAlias]]
+}
+
 // GetAllBridge returns a slice of journal cache.
 func (bm *BridgeManager) GetAllBridge() []*BridgeJournal {
-	var gwjs []*BridgeJournal
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
 
+	gwjs := make([]*BridgeJournal, 0)
 	for _, journal := range bm.journal.cache {
 		gwjs = append(gwjs, journal)
 	}
 	return gwjs
 }
 
-// GetBridge returns bridge contract of the specified address.
+// GetBridgeInfo returns bridge contract of the specified address.
 func (bm *BridgeManager) GetBridgeInfo(addr common.Address) (*BridgeInfo, bool) {
-	bm.mu.RLock()
-	defer bm.mu.RUnlock()
+	bm.bridgesMu.RLock()
+	defer bm.bridgesMu.RUnlock()
 
 	bridge, ok := bm.bridges[addr]
 	return bridge, ok
 }
 
 // DeleteBridgeInfo deletes the bridge info of the specified address.
 func (bm *BridgeManager) DeleteBridgeInfo(addr common.Address) error {
-	bm.mu.Lock()
-	defer bm.mu.Unlock()
+	bm.bridgesMu.Lock()
+	defer bm.bridgesMu.Unlock()
 
 	bi := bm.bridges[addr]
 	if bi == nil {
@@ -616,8 +679,8 @@ func (bm *BridgeManager) DeleteBridgeInfo(addr common.Address) error {
 
 // SetBridgeInfo stores the address and bridge pair with local/remote and subscription status.
 func (bm *BridgeManager) SetBridgeInfo(addr common.Address, bridge *bridgecontract.Bridge, cpAddr common.Address, cpBridge *bridgecontract.Bridge, account *accountInfo, local bool, subscribed bool) error {
-	bm.mu.Lock()
-	defer bm.mu.Unlock()
+	bm.bridgesMu.Lock()
+	defer bm.bridgesMu.Unlock()
 
 	if bm.bridges[addr] != nil {
 		return ErrDuplicatedBridgeInfo
@@ -645,6 +708,9 @@ func (bm *BridgeManager) RestoreBridges() error {
 	counter := 0
 	bm.stopAllRecoveries()
 
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
+
 	for _, journal := range bm.journal.cache {
 		cBridgeAddr := journal.ChildAddress
 		pBridgeAddr := journal.ParentAddress
@@ -723,9 +789,8 @@ func (bm *BridgeManager) RestoreBridges() error {
 }
 
 // SetJournal inserts or updates journal for a given addresses pair.
-func (bm *BridgeManager) SetJournal(localAddress, remoteAddress common.Address) error {
-	err := bm.journal.insert(localAddress, remoteAddress)
-	return err
+func (bm *BridgeManager) SetJournal(bridgeAlias string, localAddress, remoteAddress common.Address) error {
+	return bm.journal.insert(bridgeAlias, localAddress, remoteAddress)
 }
 
 // AddRecovery starts value transfer recovery for a given addresses pair.
@@ -910,6 +975,8 @@ func (bm *BridgeManager) SubscribeEvent(addr common.Address) error {
 func (bm *BridgeManager) ResetAllSubscribedEvents() error {
 	logger.Info("ResetAllSubscribedEvents is called.")
 
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
 	for _, journal := range bm.journal.cache {
 		if journal.Subscribed {
 			bm.UnsubscribeEvent(journal.ChildAddress)
@@ -942,6 +1009,9 @@ func (bm *BridgeManager) ResetAllSubscribedEvents() error {
 
 // SubscribeEvent sets watch logs and creates a goroutine loop to handle event messages.
 func (bm *BridgeManager) subscribeEvent(addr common.Address, bridge *bridgecontract.Bridge) error {
+	bm.tokenEventMu.Lock()
+	defer bm.tokenEventMu.Unlock()
+
 	chanReqVT := make(chan *bridgecontract.BridgeRequestValueTransfer, TokenEventChanSize)
 	chanReqVTencoded := make(chan *bridgecontract.BridgeRequestValueTransferEncoded, TokenEventChanSize)
 	chanHandleVT := make(chan *bridgecontract.BridgeHandleValueTransfer, TokenEventChanSize)
@@ -969,6 +1039,7 @@ func (bm *BridgeManager) subscribeEvent(addr common.Address, bridge *bridgecontr
 		return err
 	}
 	bm.withdrawEvents[addr] = withdrawnSub
+
 	bridgeInfo, ok := bm.GetBridgeInfo(addr)
 	if !ok {
 		vtEv.Unsubscribe()
@@ -987,6 +1058,9 @@ func (bm *BridgeManager) subscribeEvent(addr common.Address, bridge *bridgecontr
 
 // UnsubscribeEvent cancels the contract's watch logs and initializes the status.
 func (bm *BridgeManager) UnsubscribeEvent(addr common.Address) {
+	bm.tokenEventMu.Lock()
+	defer bm.tokenEventMu.Unlock()
+
 	receivedSub := bm.receivedEvents[addr]
 	for _, sub := range receivedSub {
 		sub.Unsubscribe()
@@ -1050,8 +1124,8 @@ func (bm *BridgeManager) loop(
 
 // Stop closes a subscribed event scope of the bridge manager.
 func (bm *BridgeManager) Stop() {
-	bm.mu.Lock()
-	defer bm.mu.Unlock()
+	bm.bridgesMu.Lock()
+	defer bm.bridgesMu.Unlock()
 
 	for addr, bi := range bm.bridges {
 		close(bi.closed)
@@ -1166,6 +1240,9 @@ func (bm *BridgeManager) GetFeeReceiver(bridgeAddr common.Address) (common.Addre
 
 // IsInParentAddrs returns true if the bridgeAddr is in the list of parent bridge addresses and returns false if not.
 func (bm *BridgeManager) IsInParentAddrs(bridgeAddr common.Address) bool {
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
+
 	for _, journal := range bm.journal.cache {
 		if journal.ParentAddress == bridgeAddr {
 			return true
@@ -1176,6 +1253,9 @@ func (bm *BridgeManager) IsInParentAddrs(bridgeAddr common.Address) bool {
 
 // IsInChildAddrs returns true if the bridgeAddr is in the list of child bridge addresses and returns false if not.
 func (bm *BridgeManager) IsInChildAddrs(bridgeAddr common.Address) bool {
+	bm.journal.cacheMu.RLock()
+	defer bm.journal.cacheMu.RUnlock()
+
 	for _, journal := range bm.journal.cache {
 		if journal.ChildAddress == bridgeAddr {
 			return true
```

### node/sc/bridge_manager_test.go
```diff
@@ -18,12 +18,14 @@ package sc
 
 import (
 	"context"
+	"encoding/hex"
 	"io/ioutil"
 	"log"
 	"math/big"
 	"math/rand"
 	"os"
 	"path"
+	"strconv"
 	"sync"
 	"testing"
 	"time"
@@ -980,7 +982,7 @@ func TestBasicJournal(t *testing.T) {
 	remoteAddr, err := bm.DeployBridgeTest(sim, 10000, false)
 	assert.NoError(t, err)
 
-	bm.SetJournal(localAddr, remoteAddr)
+	bm.SetJournal("", localAddr, remoteAddr)
 
 	ps := sc.BridgePeerSet()
 	ps.peers["test"] = nil
@@ -1072,9 +1074,9 @@ func TestMethodRestoreBridges(t *testing.T) {
 	sim.Commit()
 
 	// Set journal
-	bm.SetJournal(bridgeAddrs[0], bridgeAddrs[1])
+	bm.SetJournal("", bridgeAddrs[0], bridgeAddrs[1])
 	bm.journal.cache[bridgeAddrs[0]].Subscribed = true
-	bm.SetJournal(bridgeAddrs[2], bridgeAddrs[3])
+	bm.SetJournal("", bridgeAddrs[2], bridgeAddrs[3])
 	bm.journal.cache[bridgeAddrs[2]].Subscribed = true
 
 	ps := sc.BridgePeerSet()
@@ -1138,8 +1140,8 @@ func TestMethodGetAllBridge(t *testing.T) {
 	testBridge1 := common.BytesToAddress([]byte("test1"))
 	testBridge2 := common.BytesToAddress([]byte("test2"))
 
-	bm.journal.insert(testBridge1, testBridge2)
-	bm.journal.insert(testBridge2, testBridge1)
+	bm.journal.insert("", testBridge1, testBridge2)
+	bm.journal.insert("", testBridge2, testBridge1)
 
 	bridges := bm.GetAllBridge()
 	assert.Equal(t, 2, len(bridges))
@@ -1169,15 +1171,15 @@ func TestErrorDuplication(t *testing.T) {
 	localAddr := common.BytesToAddress([]byte("test1"))
 	remoteAddr := common.BytesToAddress([]byte("test2"))
 
-	err = bm.journal.insert(localAddr, remoteAddr)
+	err = bm.journal.insert("", localAddr, remoteAddr)
 	assert.Equal(t, nil, err)
-	err = bm.journal.insert(remoteAddr, localAddr)
+	err = bm.journal.insert("", remoteAddr, localAddr)
 	assert.Equal(t, nil, err)
 
 	// try duplicated insert.
-	err = bm.journal.insert(localAddr, remoteAddr)
+	err = bm.journal.insert("", localAddr, remoteAddr)
 	assert.NotEqual(t, nil, err)
-	err = bm.journal.insert(remoteAddr, localAddr)
+	err = bm.journal.insert("", remoteAddr, localAddr)
 	assert.NotEqual(t, nil, err)
 
 	// check cache size for checking duplication
@@ -1210,11 +1212,11 @@ func TestMethodSetJournal(t *testing.T) {
 	remoteAddr := common.BytesToAddress([]byte("test2"))
 
 	// Simple insert case
-	err = bm.SetJournal(localAddr, remoteAddr)
+	err = bm.SetJournal("", localAddr, remoteAddr)
 	assert.Equal(t, nil, err)
 
 	// Error case
-	err = bm.SetJournal(localAddr, remoteAddr)
+	err = bm.SetJournal("", localAddr, remoteAddr)
 	assert.NotEqual(t, nil, err)
 
 	// Check the number of bridge elements for checking duplication
@@ -1388,10 +1390,10 @@ func TestErrorEmptyAccount(t *testing.T) {
 	localAddr := common.BytesToAddress([]byte("test1"))
 	remoteAddr := common.BytesToAddress([]byte("test2"))
 
-	err = bm.journal.insert(localAddr, common.Address{})
+	err = bm.journal.insert("", localAddr, common.Address{})
 	assert.NotEqual(t, nil, err)
 
-	err = bm.journal.insert(common.Address{}, remoteAddr)
+	err = bm.journal.insert("", common.Address{}, remoteAddr)
 	assert.NotEqual(t, nil, err)
 
 	bm.Stop()
@@ -1463,7 +1465,7 @@ func TestErrorDupSubscription(t *testing.T) {
 
 	bm.bridges[addr], err = NewBridgeInfo(sc, addr, bridge, common.Address{}, nil, bacc.cAccount, true, true, sim)
 
-	bm.journal.cache[addr] = &BridgeJournal{addr, addr, true}
+	bm.journal.cache[addr] = &BridgeJournal{"", addr, addr, true, false}
 
 	bm.SubscribeEvent(addr)
 	err = bm.SubscribeEvent(addr)
@@ -1997,6 +1999,476 @@ func TestDecodingLegacyAnchoringTx(t *testing.T) {
 	assert.Equal(t, curBlk.Header().Number.String(), decodedData.GetBlockNumber().String())
 }
 
+func TestBridgeAliasAPIs(t *testing.T) {
+	tempDir, err := ioutil.TempDir(os.TempDir(), "sc")
+	assert.NoError(t, err)
+	defer func() {
+		if err := os.RemoveAll(tempDir); err != nil {
+			t.Fatalf("fail to delete file %v", err)
+		}
+	}()
+
+	// Generate a new random account and a funded simulator
+	aliceKey, _ := crypto.GenerateKey()
+	alice := bind.NewKeyedTransactor(aliceKey)
+	bobKey, _ := crypto.GenerateKey()
+	bob := bind.NewKeyedTransactor(bobKey)
+
+	config := &SCConfig{}
+	config.DataDir = tempDir
+
+	bacc, _ := NewBridgeAccounts(nil, tempDir, database.NewDBManager(&database.DBConfig{DBType: database.MemoryDB}), DefaultBridgeTxGasLimit, DefaultBridgeTxGasLimit)
+	bacc.pAccount.chainID = big.NewInt(0)
+	bacc.cAccount.chainID = big.NewInt(0)
+
+	alloc := blockchain.GenesisAlloc{
+		alice.From:            {Balance: big.NewInt(params.KLAY)},
+		bob.From:              {Balance: big.NewInt(params.KLAY)},
+		bacc.pAccount.address: {Balance: big.NewInt(params.KLAY)},
+		bacc.cAccount.address: {Balance: big.NewInt(params.KLAY)},
+	}
+	sim := backends.NewSimulatedBackend(alloc)
+	defer sim.Close()
+
+	sc := &SubBridge{
+		config:         config,
+		peers:          newBridgePeerSet(),
+		localBackend:   sim,
+		remoteBackend:  sim,
+		bridgeAccounts: bacc,
+	}
+
+	sc.APIBackend = &SubBridgeAPI{sc}
+	sc.handler, err = NewSubBridgeHandler(sc)
+	assert.NoError(t, err)
+
+	// Prepare manager and deploy bridge contract.
+	bm, err := NewBridgeManager(sc)
+	assert.NoError(t, err)
+	sc.handler.subbridge.bridgeManager = bm
+
+	// 1. Deploy bridge contracts and register them
+	cBridgeAddr := deployBridge(t, bm, sim, true)
+	pBridgeAddr := deployBridge(t, bm, sim, false)
+
+	// 2. Deploy token Contracts
+	cTokenAddr, _, _, err := sctoken.DeployServiceChainToken(alice, sim, cBridgeAddr)
+	assert.NoError(t, err)
+	pTokenAddr, _, _, err := sctoken.DeployServiceChainToken(alice, sim, pBridgeAddr)
+	assert.NoError(t, err)
+	sim.Commit() // block
+
+	cBridgeAddrStr := cBridgeAddr.String()
+	pBridgeAddrStr := pBridgeAddr.String()
+	cTokenAddrStr := cTokenAddr.String()
+	pTokenAddrStr := pTokenAddr.String()
+	// -------------------------- Done prepration --------------------------
+
+	// -------------------------- API test with the raw addresss format --------------------------
+	{
+		// TEST 1-1 - Success (Register bridge, tokens and subscribe registered bridges)
+		bridgePairs := bm.subBridge.APIBackend.ListBridge()
+		assert.Equal(t, len(bridgePairs), 0)
+
+		testBridgeAPIBasic(t, bm, cBridgeAddr, pBridgeAddr, nil, cTokenAddr, pTokenAddr)
+
+		bridgePairs = bm.subBridge.APIBackend.ListBridge()
+		assert.Equal(t, len(bridgePairs), 1)
+		assert.Equal(t, bridgePairs[0].Subscribed, true)
+	}
+
+	{
+		// TEST 1-2 - Failure
+		// Duplicated journal
+		testDuplicatedJournal(t, bm, cBridgeAddr, pBridgeAddr, nil)
+
+		// Duplicated token
+		testDuplicatedToken(t, bm, &cBridgeAddrStr, &pBridgeAddrStr, &cTokenAddrStr, &pTokenAddrStr)
+
+		// Already subscribed
+		testAlreadySubscribed(t, bm, &cBridgeAddrStr, &pBridgeAddrStr)
+	}
+
+	{
+		// TEST 1-3 - Success (Unsubscribe bridge, deregister bridges and tokens)
+		testUnsubscribeAndDeRegister(t, bm, &cBridgeAddrStr, &pBridgeAddrStr, &cTokenAddrStr, &pTokenAddrStr)
+	}
+
+	// -------------------------- API test with the bridge format --------------------------
+	alias := "MYBRIDGE"
+	changedAlias := "MYBRIDGE_v2"
+	invalidBridgeAlias := "0xMYBRIDGE"
+	{
+		// TEST 2-1 - Success (Register bridge, tokens and subscribe registered bridges)
+		bridgePairs := bm.subBridge.APIBackend.ListBridge()
+		assert.Equal(t, len(bridgePairs), 0)
+
+		testBridgeAPIBasic(t, bm, cBridgeAddr, pBridgeAddr, &alias, cTokenAddr, pTokenAddr)
+
+		bridgePairs = bm.subBridge.APIBackend.ListBridge()
+		assert.Equal(t, len(bridgePairs), 1)
+		assert.Equal(t, bridgePairs[0].Subscribed, true)
+		bridgePair := bm.subBridge.APIBackend.GetBridgePairByAlias(alias)
+		assert.Equal(t, bridgePair.BridgeAlias, alias)
+	}
+
+	{
+		// TEST 2-2 - Failure
+		// Duplicated bridge alias
+		testDuplicatedJournal(t, bm, cBridgeAddr, pBridgeAddr, &alias)
+
+		// Duplicated token
+		testDuplicatedToken(t, bm, &alias, &cTokenAddrStr, &pTokenAddrStr, nil)
+
+		// Already subscribed
+		testAlreadySubscribed(t, bm, &alias, nil)
+	}
+
+	{
+		// TEST 2-3 - Success (change bridge alias)
+		err = bm.subBridge.APIBackend.ChangeBridgeAlias(alias, changedAlias)
+		assert.NoError(t, err)
+
+		// Try to deregister with empty bridge alias
+		err = bm.subBridge.APIBackend.DeregisterBridge(&alias, nil)
+		assert.Equal(t, err, ErrEmptyBridgeAlias)
+
+		bridgePair := bm.subBridge.APIBackend.GetBridgePairByAlias(alias)
+		assert.Nil(t, bridgePair)
+
+		bridgePair = bm.subBridge.APIBackend.GetBridgePairByAlias(changedAlias)
+		assert.Equal(t, bridgePair.BridgeAlias, changedAlias)
+	}
+
+	{
+		// TEST 2-4 - Success (Unsubscribe bridge, deregister bridges and tokens)
+		testUnsubscribeAndDeRegister(t, bm, &changedAlias, &cTokenAddrStr, &pTokenAddrStr, nil)
+
+		// TEST 2-5 - Failure (Unsubscribe register bridge already unsubscribed)
+		err := bm.subBridge.APIBackend.UnsubscribeBridge(&changedAlias, nil)
+		assert.Equal(t, err, ErrEmptyBridgeAlias)
+	}
+
+	{
+		// TEST 2-6 - Failure (Try to create a bridge alias with invalid bridge alias name)
+		err = bm.subBridge.APIBackend.RegisterBridge(cBridgeAddr, pBridgeAddr, &invalidBridgeAlias)
+		assert.Equal(t, err, ErrNotAllowedAliasFormat)
+	}
+
+	{
+		// TEST 3 - Concurrent API Call
+		contractPairLen := 10
+		bridgeAddrs := make([]common.Address, contractPairLen)
+		tokenAddrs := make([]common.Address, contractPairLen)
+		t.Logf("Prepare %d contracts\n", contractPairLen)
+		// Preparation: Deploy bridge and token contracts
+		for i := 0; i < contractPairLen/2; i++ {
+			cBridgeAddr, pBridgeAddr = deployBridge(t, bm, sim, true), deployBridge(t, bm, sim, false)
+			cIdx, pIdx := i*2, i*2+1
+			bridgeAddrs[cIdx], bridgeAddrs[pIdx] = cBridgeAddr, pBridgeAddr
+
+			cTokenAddr, _, _, err := sctoken.DeployServiceChainToken(alice, sim, cBridgeAddr)
+			assert.NoError(t, err)
+			pTokenAddr, _, _, err := sctoken.DeployServiceChainToken(alice, sim, pBridgeAddr)
+			assert.NoError(t, err)
+			tokenAddrs[cIdx], tokenAddrs[pIdx] = cTokenAddr, pTokenAddr
+
+			t.Logf("Deployed bridge contracts %d, %d\n", cIdx, pIdx)
+		}
+
+		// Declare another bridge and token contracts that did not initialize
+		fixedChildBridgeAddr, fixedParentBridgeAddr := deployBridge(t, bm, sim, true), deployBridge(t, bm, sim, false)
+
+		const (
+			BRIDGE_SETUP = iota
+			FAILURE
+			CLEANUP_BRIDGE
+			ALIAS_BRIDGE_SETUP
+			ALIAS_FAILURE
+			ALIAS_CLEANUP_BRIDGE
+			REGISTER_MULTIPLE_TOKEN_WITH_SINGLE_BRIDGE
+		)
+		// DO NOT CHANGE THE TEST ORDER
+		testCases := map[uint8]string{
+			BRIDGE_SETUP:         "BRIDGE_SETUP",
+			FAILURE:              "FAILURE",
+			CLEANUP_BRIDGE:       "CLEANUP_BRIDGE",
+			ALIAS_BRIDGE_SETUP:   "ALIAS_BRIDGE_SETUP",
+			ALIAS_FAILURE:        "ALIAS_FAILURE",
+			ALIAS_CLEANUP_BRIDGE: "ALIAS_CLEANUP_BRIDGE",
+			REGISTER_MULTIPLE_TOKEN_WITH_SINGLE_BRIDGE: "REGISTER_MULTIPLE_TOKEN_WITH_SINGLE_BRIDGE",
+		}
+
+		for testNum := 0; testNum < len(testCases); testNum++ {
+			wg := sync.WaitGroup{}
+			wg.Add(contractPairLen / 2)
+			for i := 0; i < len(bridgeAddrs); i += 2 {
+				cIdx, pIdx := i, i+1
+				go func(cIdx, pIdx int) {
+					cBridgeAddr, pBridgeAddr := bridgeAddrs[cIdx], bridgeAddrs[pIdx]
+					cBridgeAddrStr, pBridgeAddrStr := cBridgeAddr.String(), pBridgeAddr.String()
+					cTokenAddr, pTokenAddr := tokenAddrs[cIdx], tokenAddrs[pIdx]
+					cTokenAddrStr, pTokenAddrStr := cTokenAddr.String(), pTokenAddr.String()
+					alias := "MYBRIDGE_v3" + strconv.Itoa(cIdx)
+
+					switch testNum {
+					case BRIDGE_SETUP:
+						// TEST 3-1. `testBridgeAPIBasic` again with concurrent calls using raw-address-format APIS
+						testBridgeAPIBasic(t, bm, cBridgeAddr, pBridgeAddr, nil, cTokenAddr, pTokenAddr)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					case FAILURE:
+						// TEST 3-2 - Failure
+						testDuplicatedJournal(t, bm, cBridgeAddr, pBridgeAddr, nil)
+						testDuplicatedToken(t, bm, &cBridgeAddrStr, &pBridgeAddrStr, &cTokenAddrStr, &pTokenAddrStr)
+						testAlreadySubscribed(t, bm, &cBridgeAddrStr, &pBridgeAddrStr)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					case ALIAS_BRIDGE_SETUP:
+						// TEST 3-3. `testBridgeAPIBasic` again with concurrent calls using alias APIS
+						testBridgeAPIBasic(t, bm, cBridgeAddr, pBridgeAddr, &alias, cTokenAddr, pTokenAddr)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					case ALIAS_FAILURE:
+						// TEST 3-4 - Failure
+						testDuplicatedJournal(t, bm, cBridgeAddr, pBridgeAddr, &alias)
+						testDuplicatedToken(t, bm, &alias, &cTokenAddrStr, &pTokenAddrStr, nil)
+						testAlreadySubscribed(t, bm, &alias, nil)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					case CLEANUP_BRIDGE:
+						// TEST 3-5 - Success (Unsubscribe bridge, deregister bridges and tokens)
+						testUnsubscribeAndDeRegister(t, bm, &cBridgeAddrStr, &pBridgeAddrStr, &cTokenAddrStr, &pTokenAddrStr)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					case ALIAS_CLEANUP_BRIDGE:
+						// TEST 3-6 - Success (Unsubscribe bridge, deregister bridges and tokens)
+						testUnsubscribeAndDeRegister(t, bm, &alias, &cTokenAddrStr, &pTokenAddrStr, nil)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					case REGISTER_MULTIPLE_TOKEN_WITH_SINGLE_BRIDGE:
+						// TEST 3-7 - Use the fresh bridge that did not register any token contracts
+						cbAddr, pbAddr := fixedChildBridgeAddr.String(), fixedParentBridgeAddr.String()
+						testRegisterToken(t, bm, &cbAddr, &pbAddr, &cTokenAddrStr, &pTokenAddrStr)
+						t.Log("passed:", testCases[uint8(testNum)], cIdx, pIdx)
+					}
+					wg.Done()
+				}(cIdx, pIdx)
+			}
+			wg.Wait()
+			t.Log("Test Done: ", testCases[uint8(testNum)])
+			// Check the status of conccurent calls with a signle thread
+			switch testNum {
+			case BRIDGE_SETUP:
+				checkBridgeSetup(t, bm, true, 1, contractPairLen/2)
+			case CLEANUP_BRIDGE:
+				checkBridgeSetup(t, bm, false, 0, 0)
+			case ALIAS_BRIDGE_SETUP:
+				checkBridgeSetup(t, bm, true, 1, contractPairLen/2)
+			case ALIAS_CLEANUP_BRIDGE:
+				checkBridgeSetup(t, bm, false, 0, 0)
+				// Initiailize another two bridge contracts for the test `REGISTER_MULTIPLE_TOKEN_WITH_SINGLE_BRIDGE`
+				err = bm.subBridge.APIBackend.RegisterBridge(fixedChildBridgeAddr, fixedParentBridgeAddr, nil)
+				assert.NoError(t, err)
+			case REGISTER_MULTIPLE_TOKEN_WITH_SINGLE_BRIDGE:
+				checkRegisterMultipleToken(t, bm, fixedChildBridgeAddr, fixedParentBridgeAddr, contractPairLen/2)
+			}
+		}
+		t.Log("All Done")
+	}
+}
+
+func testBridgeAPIBasic(t *testing.T, bm *BridgeManager,
+	cBridgeAddr, pBridgeAddr common.Address,
+	alias *string,
+	cTokenAddr, pTokenAddr common.Address,
+) {
+	// TEST 1 - Success (Register bridge, tokens and subscribe registered bridges)
+	cBridgeAddrStr := cBridgeAddr.String()
+	pBridgeAddrStr := pBridgeAddr.String()
+	cTokenAddrStr := cTokenAddr.String()
+	pTokenAddrStr := pTokenAddr.String()
+
+	// Register Bridge
+	err := bm.subBridge.APIBackend.RegisterBridge(cBridgeAddr, pBridgeAddr, alias)
+	assert.NoError(t, err)
+
+	// Register tokens
+	if alias != nil {
+		err = bm.subBridge.APIBackend.RegisterToken(alias, &cTokenAddrStr, &pTokenAddrStr, nil)
+	} else {
+		err = bm.subBridge.APIBackend.RegisterToken(&cBridgeAddrStr, &pBridgeAddrStr, &cTokenAddrStr, &pTokenAddrStr)
+	}
+	assert.NoError(t, err)
+
+	// Subscribe bridges
+	if alias != nil {
+		err = bm.subBridge.APIBackend.SubscribeBridge(alias, nil)
+	} else {
+		err = bm.subBridge.APIBackend.SubscribeBridge(&cBridgeAddrStr, &pBridgeAddrStr)
+	}
+	assert.NoError(t, err)
+}
+
+func testDuplicatedJournal(t *testing.T, bm *BridgeManager, cBridgeAddr, pBridgeAddr common.Address, alias *string) {
+	err := bm.subBridge.APIBackend.RegisterBridge(cBridgeAddr, pBridgeAddr, alias)
+	if err != ErrDuplicatedJournal && err != ErrDuplicatedAlias {
+		t.Fatal("Unexpected error", err)
+	}
+}
+
+func testDuplicatedToken(t *testing.T, bm *BridgeManager, cBridgeAddrStr, pBridgeAddrStr, cTokenAddrStr, pTokenAddrStr *string) {
+	err := bm.subBridge.APIBackend.RegisterToken(cBridgeAddrStr, pBridgeAddrStr, cTokenAddrStr, pTokenAddrStr)
+	assert.Equal(t, err, ErrDuplicatedToken)
+}
+
+func testAlreadySubscribed(t *testing.T, bm *BridgeManager, cBridgeAddrStr, pBridgeAddrStr *string) {
+	err := bm.subBridge.APIBackend.SubscribeBridge(cBridgeAddrStr, pBridgeAddrStr)
+	assert.Equal(t, err, ErrAlreadySubscribed)
+}
+
+func testRegisterToken(t *testing.T, bm *BridgeManager, cBridgeAddrStr, pBridgeAddrStr, cTokenAddrStr, pTokenAddrStr *string) {
+	err := bm.subBridge.APIBackend.RegisterToken(cBridgeAddrStr, pBridgeAddrStr, cTokenAddrStr, pTokenAddrStr)
+	assert.NoError(t, err)
+}
+
+func testUnsubscribeAndDeRegister(t *testing.T, bm *BridgeManager,
+	cBridgeAddrStr, pBridgeAddrStr, cTokenAddrStr, pTokenAddrStr *string,
+) {
+	findBridgePair := func(addrStr string) *BridgeJournal {
+		bridgePairs := bm.subBridge.APIBackend.ListBridge()
+		for _, bridgePair := range bridgePairs {
+			if bridgePair.ChildAddress.String() == addrStr || bridgePair.BridgeAlias == addrStr {
+				return bridgePair
+			}
+		}
+		return nil
+	}
+	bridgePairLen := len(bm.subBridge.APIBackend.ListBridge())
+	defer func() {
+		err := bm.subBridge.APIBackend.DeregisterBridge(cBridgeAddrStr, pBridgeAddrStr)
+		assert.NoError(t, err)
+		assert.Equal(t, len(bm.subBridge.APIBackend.ListBridge()) < bridgePairLen, true)
+	}()
+
+	bridgePair := findBridgePair(*cBridgeAddrStr)
+	assert.NotNil(t, bridgePair)
+	assert.Equal(t, bridgePair.Subscribed, true)
+	err := bm.subBridge.APIBackend.UnsubscribeBridge(cBridgeAddrStr, pBridgeAddrStr)
+	assert.NoError(t, err)
+	assert.Equal(t, bridgePair.Subscribed, false)
+
+	cBi, ok := bm.GetBridgeInfo(bridgePair.ChildAddress)
+	assert.Equal(t, ok, true)
+	assert.Equal(t, len(cBi.counterpartToken), 1)
+	pBi, ok := bm.GetBridgeInfo(bridgePair.ParentAddress)
+	assert.Equal(t, ok, true)
+	assert.Equal(t, len(pBi.counterpartToken), 1)
+
+	err = bm.subBridge.APIBackend.DeregisterToken(cBridgeAddrStr, pBridgeAddrStr, cTokenAddrStr, pTokenAddrStr)
+	assert.NoError(t, err)
+	assert.Equal(t, len(cBi.counterpartToken), 0)
+	assert.Equal(t, len(pBi.counterpartToken), 0)
+}
+
+func TestLegacyBridgeJournalDecode(t *testing.T) {
+	// `encodedJournalHexStr` is an encoded legacy bridge journals. The code below generate the following hex.
+	encodedJournalHexStr := "eb9485564429cce278d4399436f1af2f91e1be6f0bd494c12701e0cb09d6600f774be1dbb585ddc749f9da80eb9485564429cce278d4399436f1af2f91e1be6f0bd594c12701e0cb09d6600f774be1dbb585ddc749f9db01eb9485564429cce278d4399436f1af2f91e1be6f0bd694c12701e0cb09d6600f774be1dbb585ddc749f9dc01"
+	/*
+		legacyJournals := []BridgeJournal{
+			{
+				ChildAddress:  common.HexToAddress("0x85564429cce278d4399436f1af2f91e1be6f0bd4"),
+				ParentAddress: common.HexToAddress("0xc12701e0cb09d6600f774be1dbb585ddc749f9da"),
+				Subscribed:    false,
+			},
+			{
+				ChildAddress:  common.HexToAddress("0x85564429cce278d4399436f1af2f91e1be6f0bd5"),
+				ParentAddress: common.HexToAddress("0xc12701e0cb09d6600f774be1dbb585ddc749f9db"),
+				Subscribed:    true,
+			},
+			{
+				ChildAddress:  common.HexToAddress("0x85564429cce278d4399436f1af2f91e1be6f0bd6"),
+				ParentAddress: common.HexToAddress("0xc12701e0cb09d6600f774be1dbb585ddc749f9dc"),
+				Subscribed:    true,
+			},
+		}
+			encodedBuf := new(bytes.Buffer)
+			for i := 0; i < len(journals); i++ {
+				err := rlp.Encode(encodedBuf, &journals[i])
+				assert.NoError(t, err)
+			}
+			encodedString := hex.EncodeToString(encodedBuf.Bytes())
+			fmt.Println(encodedString)
+	*/
+
+	legacyJournals := []BridgeJournal{
+		{
+			ChildAddress:  common.HexToAddress("0x85564429cce278d4399436f1af2f91e1be6f0bd4"),
+			ParentAddress: common.HexToAddress("0xc12701e0cb09d6600f774be1dbb585ddc749f9da"),
+			Subscribed:    false,
+		},
+		{
+			ChildAddress:  common.HexToAddress("0x85564429cce278d4399436f1af2f91e1be6f0bd5"),
+			ParentAddress: common.HexToAddress("0xc12701e0cb09d6600f774be1dbb585ddc749f9db"),
+			Subscribed:    true,
+		},
+		{
+			ChildAddress:  common.HexToAddress("0x85564429cce278d4399436f1af2f91e1be6f0bd6"),
+			ParentAddress: common.HexToAddress("0xc12701e0cb09d6600f774be1dbb585ddc749f9dc"),
+			Subscribed:    true,
+		},
+	}
+
+	tempJournalPath := "legacy-journal-decoding-test"
+	tempFile, err := ioutil.TempFile(".", tempJournalPath)
+	assert.NoError(t, err)
+
+	encodedHex, err := hex.DecodeString(encodedJournalHexStr)
+	assert.NoError(t, err)
+
+	_, err = tempFile.Write(encodedHex)
+	assert.NoError(t, err)
+	defer os.Remove(tempFile.Name())
+
+	readJournalIdx := 0
+	load := func(gwjournal BridgeJournal) error {
+		assert.Equal(t, len(gwjournal.BridgeAlias), 0)
+		assert.Equal(t, gwjournal.ChildAddress.String(), legacyJournals[readJournalIdx].ChildAddress.String())
+		assert.Equal(t, gwjournal.ParentAddress.String(), legacyJournals[readJournalIdx].ParentAddress.String())
+		assert.Equal(t, gwjournal.Subscribed, legacyJournals[readJournalIdx].Subscribed)
+		readJournalIdx++
+		return nil
+	}
+	journalAddr := newBridgeAddrJournal(tempFile.Name())
+	err = journalAddr.load(load)
+	assert.NoError(t, err)
+}
+
+func checkBridgeSetup(t *testing.T, bm *BridgeManager, expectedSubscribed bool, expectedNumberOfToken, expectedBridgeLen int) {
+	bridgePairs := bm.subBridge.APIBackend.ListBridge()
+	assert.Equal(t, len(bridgePairs), expectedBridgeLen)
+	for _, bridgePair := range bridgePairs {
+		assert.Equal(t, bridgePair.Subscribed, expectedSubscribed)
+		cbi, ok := bm.GetBridgeInfo(bridgePair.ChildAddress)
+		assert.Equal(t, ok, true)
+		pbi, ok := bm.GetBridgeInfo(bridgePair.ChildAddress)
+		assert.Equal(t, ok, true)
+		assert.Equal(t, len(cbi.counterpartToken), expectedNumberOfToken)
+		assert.Equal(t, len(pbi.counterpartToken), expectedNumberOfToken)
+	}
+}
+
+func checkRegisterMultipleToken(t *testing.T, bm *BridgeManager, cBridgeAddr, pBridgeAddr common.Address, expectedLen int) {
+	cbi, ok := bm.GetBridgeInfo(cBridgeAddr)
+	assert.Equal(t, ok, true)
+	pbi, ok := bm.GetBridgeInfo(pBridgeAddr)
+	assert.Equal(t, ok, true)
+	assert.Equal(t, len(cbi.counterpartToken), expectedLen)
+	assert.Equal(t, len(pbi.counterpartToken), expectedLen)
+}
+
+func randomHex(n int) (string, error) {
+	bytes := make([]byte, n)
+	if _, err := rand.Read(bytes); err != nil {
+		return "", err
+	}
+	return hex.EncodeToString(bytes), nil
+}
+
 func TestBridgeAddressType(t *testing.T) {
 	tempDir, err := ioutil.TempDir(os.TempDir(), "sc")
 	assert.NoError(t, err)
@@ -2144,6 +2616,37 @@ func (bm *BridgeManager) DeployBridgeTest(backend *backends.SimulatedBackend, am
 	return addr, err
 }
 
+// deployBridge deploys bridge contract and returns its address
+func deployBridge(t *testing.T, bm *BridgeManager, backend *backends.SimulatedBackend, local bool) common.Address {
+	var acc *accountInfo
+
+	// When the pending block of backend is updated, commit it
+	// bm.DeployBridge will be waiting until the block is committed
+	pendingBlock := backend.PendingBlock()
+	go func() {
+		for pendingBlock == backend.PendingBlock() {
+			time.Sleep(100 * time.Millisecond)
+		}
+		backend.Commit()
+		return
+	}()
+
+	// Set transfer value of the bridge account
+	if local {
+		acc = bm.subBridge.bridgeAccounts.cAccount
+	} else {
+		acc = bm.subBridge.bridgeAccounts.pAccount
+	}
+
+	auth := acc.GenerateTransactOpts()
+	auth.Value = big.NewInt(10000)
+
+	// Deploy a bridge contract
+	_, addr, err := bm.DeployBridge(auth, backend, local)
+	assert.NoError(t, err)
+	return addr
+}
+
 func isExpectedBalance(t *testing.T, bridgeManager *BridgeManager,
 	pBridgeAddr, cBridgeAddr common.Address,
 	expectedParentBridgeBalance, expectedChildBridgeBalance int64,
@@ -2206,7 +2709,7 @@ func TestGetBridgeContractBalance(t *testing.T) {
 		assert.NoError(t, err)
 		pBridgeAddr, err := bm.DeployBridgeTest(sim, initialParentbridgeBalance, false)
 		assert.NoError(t, err)
-		bm.SetJournal(cBridgeAddr, pBridgeAddr)
+		bm.SetJournal("", cBridgeAddr, pBridgeAddr)
 		assert.NoError(t, err)
 		sim.Commit()
 		isExpectedBalance(t, bm, pBridgeAddr, cBridgeAddr, initialParentbridgeBalance, initialChildbridgeBalance)
@@ -2221,7 +2724,7 @@ func TestGetBridgeContractBalance(t *testing.T) {
 			assert.NoError(t, err)
 			pBridgeAddr, err := bm.DeployBridgeTest(sim, initialParentbridgeBalance, false)
 			assert.NoError(t, err)
-			bm.SetJournal(cBridgeAddr, pBridgeAddr)
+			bm.SetJournal("", cBridgeAddr, pBridgeAddr)
 			assert.NoError(t, err)
 			sim.Commit()
 			isExpectedBalance(t, bm, pBridgeAddr, cBridgeAddr, initialParentbridgeBalance, initialChildbridgeBalance)
```

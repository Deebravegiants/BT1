# [?] make oracleFactoryDB type thread safe to fix CAPPL-1062 - core node panic (#19527)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-09-24
Source: https://github.com/smartcontractkit/chainlink/commit/7cd09938fa1a6d331545881dc43f4183a6d9cf4e
Type: security-commit

## Details
make oracleFactoryDB type thread safe to fix CAPPL-1062 - core node panic (#19527)

* make thread oracleFactoryDB type thread safe to fix CAPPL-1062

* tidy

## Patch
### core/services/ocr2/plugins/generic/oraclefactorydb.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 	"encoding/json"
 	"fmt"
+	"sync"
 	"time"
 
 	ocrtypes "github.com/smartcontractkit/libocr/offchainreporting2plus/types"
@@ -21,6 +22,8 @@ type oracleFactoryDb struct {
 	states               map[ocrtypes.ConfigDigest]*ocrtypes.PersistentState
 	pendingTransmissions map[ocrtypes.ReportTimestamp]ocrtypes.PendingTransmission
 	protocolStates       map[ocrtypes.ConfigDigest]map[string][]byte
+
+	mu sync.Mutex
 }
 
 var (
@@ -39,6 +42,9 @@ func OracleFactoryDB(specID int32, lggr logger.Logger) *oracleFactoryDb {
 }
 
 func (ofdb *oracleFactoryDb) ReadState(ctx context.Context, cd ocrtypes.ConfigDigest) (ps *ocrtypes.PersistentState, err error) {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	ps, ok := ofdb.states[cd]
 	if !ok {
 		return nil, fmt.Errorf("state not found for standard capabilities spec ID %d, config digest %s", ofdb.specID, cd)
@@ -48,11 +54,17 @@ func (ofdb *oracleFactoryDb) ReadState(ctx context.Context, cd ocrtypes.ConfigDi
 }
 
 func (ofdb *oracleFactoryDb) WriteState(ctx context.Context, cd ocrtypes.ConfigDigest, state ocrtypes.PersistentState) error {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	ofdb.states[cd] = &state
 	return nil
 }
 
 func (ofdb *oracleFactoryDb) ReadConfig(ctx context.Context) (c *ocrtypes.ContractConfig, err error) {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	if ofdb.config == nil {
 		// Returning nil, nil because this is a cache miss
 		return nil, nil
@@ -61,6 +73,9 @@ func (ofdb *oracleFactoryDb) ReadConfig(ctx context.Context) (c *ocrtypes.Contra
 }
 
 func (ofdb *oracleFactoryDb) WriteConfig(ctx context.Context, c ocrtypes.ContractConfig) error {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	ofdb.config = &c
 
 	cBytes, err := json.Marshal(c)
@@ -74,11 +89,17 @@ func (ofdb *oracleFactoryDb) WriteConfig(ctx context.Context, c ocrtypes.Contrac
 }
 
 func (ofdb *oracleFactoryDb) StorePendingTransmission(ctx context.Context, t ocrtypes.ReportTimestamp, tx ocrtypes.PendingTransmission) error {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	ofdb.pendingTransmissions[t] = tx
 	return nil
 }
 
 func (ofdb *oracleFactoryDb) PendingTransmissionsWithConfigDigest(ctx context.Context, cd ocrtypes.ConfigDigest) (map[ocrtypes.ReportTimestamp]ocrtypes.PendingTransmission, error) {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	m := make(map[ocrtypes.ReportTimestamp]ocrtypes.PendingTransmission)
 	for k, v := range ofdb.pendingTransmissions {
 		if k.ConfigDigest == cd {
@@ -90,11 +111,17 @@ func (ofdb *oracleFactoryDb) PendingTransmissionsWithConfigDigest(ctx context.Co
 }
 
 func (ofdb *oracleFactoryDb) DeletePendingTransmission(ctx context.Context, t ocrtypes.ReportTimestamp) error {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	delete(ofdb.pendingTransmissions, t)
 	return nil
 }
 
 func (ofdb *oracleFactoryDb) DeletePendingTransmissionsOlderThan(ctx context.Context, t time.Time) error {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	for k, v := range ofdb.pendingTransmissions {
 		if v.Time.Before(t) {
 			delete(ofdb.pendingTransmissions, k)
@@ -109,6 +136,9 @@ func (ofdb *oracleFactoryDb) ReadProtocolState(
 	configDigest ocrtypes.ConfigDigest,
 	key string,
 ) ([]byte, error) {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	value, ok := ofdb.protocolStates[configDigest][key]
 	if !ok {
 		// Previously implementation returned nil if the state is not found
@@ -123,6 +153,9 @@ func (ofdb *oracleFactoryDb) WriteProtocolState(
 	key string,
 	value []byte,
 ) error {
+	ofdb.mu.Lock()
+	defer ofdb.mu.Unlock()
+
 	if value == nil {
 		delete(ofdb.protocolStates[configDigest], key)
 	} else {
```

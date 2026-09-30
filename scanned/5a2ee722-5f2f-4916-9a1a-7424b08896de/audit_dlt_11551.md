# [?] Add verification to prevent GetHeaderV1 method to crash (#101)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/mev-boost
Published: 2022-04-24
Source: https://github.com/flashbots/mev-boost/commit/63daa518f600d6a4aeeeefa562a98bf062052fdc
Type: security-commit

## Details
Add verification to prevent GetHeaderV1 method to crash (#101)

Signed-off-by: Luca Georges Francois <luca.georges-francois@epitech.eu>

## Patch
### lib/e2e_test.go
```diff
@@ -215,6 +215,21 @@ func TestE2E_GetHeader(t *testing.T) {
 	assert.Equal(t, "12345", res.Message.Value.String())
 }
 
+func TestE2E_GetHeaderError(t *testing.T) {
+	relay1 := setupMockRelay()
+	server, err := newTestBoostRPCServer([]string{relay1.URL})
+	require.Nil(t, err, err)
+	defer server.Stop()
+
+	client := gethRpc.DialInProc(server)
+	defer client.Close()
+
+	res := new(GetHeaderResponse)
+	err = client.Call(&res, "builder_getHeaderV1", nil)
+	require.Error(t, err)
+	require.Equal(t, err.Error(), errNoBlockHash.Error())
+}
+
 func TestE2E_GetPayload(t *testing.T) {
 	relay1, relay2 := setupMockRelay(), setupMockRelay()
 	server, err := newTestBoostRPCServer([]string{relay1.URL, relay2.URL})
```

### lib/service.go
```diff
@@ -19,6 +19,10 @@ var (
 	defaultGetHeaderTimeout = time.Second * 2
 )
 
+var (
+	errNoBlockHash = errors.New("no blockhash provided")
+)
+
 // BoostService TODO
 type BoostService struct {
 	relayURLs []string
@@ -141,6 +145,10 @@ func (m *BoostService) GetHeaderV1(ctx context.Context, blockHash *string) (*Get
 	method := "builder_getHeaderV1"
 	logMethod := m.log.WithField("method", method)
 
+	if blockHash == nil {
+		return nil, errNoBlockHash
+	}
+
 	if len(*blockHash) != 66 {
 		return nil, fmt.Errorf("invalid block hash: %s", *blockHash)
 	}
```

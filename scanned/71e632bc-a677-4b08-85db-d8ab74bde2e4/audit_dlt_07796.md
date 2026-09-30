# [?] fix panic when the rpc client is not initialized (#11528)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-10-05
Source: https://github.com/OffchainLabs/prysm/commit/c1446a35c51ea49346d8cbfffd2fa9b6dd75ad67
Type: security-commit

## Details
fix panic when the rpc client is not initialized (#11528)

Co-authored-by: Nishant Das <nishdas93@gmail.com>
Co-authored-by: Your Name <you@example.com>

## Patch
### beacon-chain/execution/service.go
```diff
@@ -112,6 +112,18 @@ type RPCClient interface {
 	CallContext(ctx context.Context, result interface{}, method string, args ...interface{}) error
 }
 
+type RPCClientEmpty struct {
+}
+
+func (RPCClientEmpty) Close() {}
+func (RPCClientEmpty) BatchCall([]gethRPC.BatchElem) error {
+	return errors.New("rpc client is not initialized")
+}
+
+func (RPCClientEmpty) CallContext(context.Context, interface{}, string, ...interface{}) error {
+	return errors.New("rpc client is not initialized")
+}
+
 // config defines a config struct for dependencies into the service.
 type config struct {
 	depositContractAddr     common.Address
@@ -169,8 +181,9 @@ func NewService(ctx context.Context, opts ...Option) (*Service, error) {
 	}
 
 	s := &Service{
-		ctx:    ctx,
-		cancel: cancel,
+		ctx:       ctx,
+		cancel:    cancel,
+		rpcClient: RPCClientEmpty{},
 		cfg: &config{
 			beaconNodeStatsUpdater: &NopBeaconNodeStatsUpdater{},
 			eth1HeaderReqLimit:     defaultEth1HeaderReqLimit,
```

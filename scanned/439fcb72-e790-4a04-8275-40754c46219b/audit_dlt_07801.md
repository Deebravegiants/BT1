# [?] Fix Eth1Connection API Panic (#10938)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-06-27
Source: https://github.com/OffchainLabs/prysm/commit/3a841a84672c0bc82f22f789354acf54f1c25538
Type: security-commit

## Details
Fix Eth1Connection API Panic (#10938)

Co-authored-by: prylabs-bulldozer[bot] <58059840+prylabs-bulldozer[bot]@users.noreply.github.com>

## Patch
### beacon-chain/rpc/prysm/v1alpha1/node/server.go
```diff
@@ -224,6 +224,7 @@ func (ns *Server) ListPeers(ctx context.Context, _ *empty.Empty) (*ethpb.Peers,
 // GetETH1ConnectionStatus gets data about the ETH1 endpoints.
 func (ns *Server) GetETH1ConnectionStatus(_ context.Context, _ *empty.Empty) (*ethpb.ETH1ConnectionStatus, error) {
 	var errStrs []string
+	var currErrString string
 	errs := ns.POWChainInfoFetcher.ETH1ConnectionErrors()
 	// Extract string version of the errors.
 	for _, err := range errs {
@@ -233,9 +234,13 @@ func (ns *Server) GetETH1ConnectionStatus(_ context.Context, _ *empty.Empty) (*e
 			errStrs = append(errStrs, err.Error())
 		}
 	}
+	curErr := ns.POWChainInfoFetcher.CurrentETH1ConnectionError()
+	if curErr != nil {
+		currErrString = curErr.Error()
+	}
 	return &ethpb.ETH1ConnectionStatus{
 		CurrentAddress:         ns.POWChainInfoFetcher.CurrentETH1Endpoint(),
-		CurrentConnectionError: ns.POWChainInfoFetcher.CurrentETH1ConnectionError().Error(),
+		CurrentConnectionError: currErrString,
 		Addresses:              ns.POWChainInfoFetcher.ETH1Endpoints(),
 		ConnectionErrors:       errStrs,
 	}, nil
```

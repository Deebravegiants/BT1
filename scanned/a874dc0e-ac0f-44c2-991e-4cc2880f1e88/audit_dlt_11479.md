# [?] Fix data race during rly paths list (#614)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/relayer
Published: 2022-03-23
Source: https://github.com/cosmos/relayer/commit/e5c972cca94eaf12afa6c7ec17102ab0bdc41c2f
Type: security-commit

## Details
Fix data race during rly paths list (#614)

There was one error that was being concurrently assigned during several
goroutines, so use distinct error values with narrow scoping instead.

Co-authored-by: Jack Zampolin <jack.zampolin@gmail.com>

## Patch
### relayer/path.go
```diff
@@ -170,7 +170,6 @@ type PathWithStatus struct {
 // the current status of the path
 func (p *Path) QueryPathStatus(ctx context.Context, src, dst *Chain) *PathWithStatus {
 	var (
-		err              error
 		eg               errgroup.Group
 		srch, dsth       int64
 		srcCs, dstCs     *clienttypes.QueryClientStateResponse
@@ -179,46 +178,52 @@ func (p *Path) QueryPathStatus(ctx context.Context, src, dst *Chain) *PathWithSt
 		out = &PathWithStatus{Path: p, Status: PathStatus{false, false, false}}
 	)
 	eg.Go(func() error {
+		var err error
 		srch, err = src.ChainProvider.QueryLatestHeight(ctx)
 		return err
 	})
 	eg.Go(func() error {
+		var err error
 		dsth, err = dst.ChainProvider.QueryLatestHeight(ctx)
 		return err
 	})
-	if err = eg.Wait(); err != nil {
+	if err := eg.Wait(); err != nil {
 		return out
 	}
 	out.Status.Chains = true
-	if err = src.SetPath(p.Src); err != nil {
+	if err := src.SetPath(p.Src); err != nil {
 		return out
 	}
-	if err = dst.SetPath(p.Dst); err != nil {
+	if err := dst.SetPath(p.Dst); err != nil {
 		return out
 	}
 
 	eg.Go(func() error {
+		var err error
 		srcCs, err = src.ChainProvider.QueryClientStateResponse(srch, src.ClientID())
 		return err
 	})
 	eg.Go(func() error {
+		var err error
 		dstCs, err = dst.ChainProvider.QueryClientStateResponse(dsth, dst.ClientID())
 		return err
 	})
-	if err = eg.Wait(); err != nil || srcCs == nil || dstCs == nil {
+	if err := eg.Wait(); err != nil || srcCs == nil || dstCs == nil {
 		return out
 	}
 	out.Status.Clients = true
 
 	eg.Go(func() error {
+		var err error
 		srcConn, err = src.ChainProvider.QueryConnection(srch, src.ConnectionID())
 		return err
 	})
 	eg.Go(func() error {
+		var err error
 		dstConn, err = dst.ChainProvider.QueryConnection(dsth, dst.ConnectionID())
 		return err
 	})
-	if err = eg.Wait(); err != nil || srcConn.Connection.State != conntypes.OPEN ||
+	if err := eg.Wait(); err != nil || srcConn.Connection.State != conntypes.OPEN ||
 		dstConn.Connection.State != conntypes.OPEN {
 		return out
 	}
```

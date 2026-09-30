# [?] light: fix panic with RPC calls to commit and validator when height is nil (#6040)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2021-02-04
Source: https://github.com/cometbft/cometbft/commit/3c22ed832048c94b36f84b05429665b99697612a
Type: security-commit

## Details
light: fix panic with RPC calls to commit and validator when height is nil (#6040)

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -25,3 +25,5 @@ Friendly reminder, we have a [bug bounty program](https://hackerone.com/tendermi
 ### BUG FIXES
 
 - [light] \#6022 Fix a bug when the number of validators equals 100 (@melekes)
+- [light] \#6026 Fix a bug when height isn't provided for the rpc calls: `/commit` and `/validators` (@cmwaters)
+
```

### light/provider/http/http.go
```diff
@@ -75,7 +75,7 @@ func (p *http) LightBlock(ctx context.Context, height int64) (*types.LightBlock,
 		return nil, err
 	}
 
-	vs, err := p.validatorSet(ctx, h)
+	vs, err := p.validatorSet(ctx, &sh.Height)
 	if err != nil {
 		return nil, err
 	}
```

### light/rpc/client.go
```diff
@@ -26,8 +26,10 @@ var errNegOrZeroHeight = errors.New("negative or zero height")
 type KeyPathFunc func(path string, key []byte) (merkle.KeyPath, error)
 
 // LightClient is an interface that contains functionality needed by Client from the light client.
+//go:generate mockery --case underscore --name LightClient
 type LightClient interface {
 	ChainID() string
+	Update(ctx context.Context, now time.Time) (*types.LightBlock, error)
 	VerifyLightBlockAtHeight(ctx context.Context, height int64, now time.Time) (*types.LightBlock, error)
 	TrustedLightBlock(height int64) (*types.LightBlock, error)
 }
@@ -130,7 +132,8 @@ func (c *Client) ABCIQueryWithOptions(ctx context.Context, path string, data tmb
 
 	// Update the light client if we're behind.
 	// NOTE: AppHash for height H is in header H+1.
-	l, err := c.updateLightClientIfNeededTo(ctx, resp.Height+1)
+	nextHeight := resp.Height + 1
+	l, err := c.updateLightClientIfNeededTo(ctx, &nextHeight)
 	if err != nil {
 		return nil, err
 	}
@@ -213,7 +216,7 @@ func (c *Client) ConsensusParams(ctx context.Context, height *int64) (*ctypes.Re
 	}
 
 	// Update the light client if we're behind.
-	l, err := c.updateLightClientIfNeededTo(ctx, res.BlockHeight)
+	l, err := c.updateLightClientIfNeededTo(ctx, &res.BlockHeight)
 	if err != nil {
 		return nil, err
 	}
@@ -252,7 +255,7 @@ func (c *Client) BlockchainInfo(ctx context.Context, minHeight, maxHeight int64)
 	// Update the light client if we're behind.
 	if len(res.BlockMetas) > 0 {
 		lastHeight := res.BlockMetas[len(res.BlockMetas)-1].Header.Height
-		if _, err := c.updateLightClientIfNeededTo(ctx, lastHeight); err != nil {
+		if _, err := c.updateLightClientIfNeededTo(ctx, &lastHeight); err != nil {
 			return nil, err
 		}
 	}
@@ -296,7 +299,7 @@ func (c *Client) Block(ctx context.Context, height *int64) (*ctypes.ResultBlock,
 	}
 
 	// Update the light client if we're behind.
-	l, err := c.updateLightClientIfNeededTo(ctx, res.Block.Height)
+	l, err := c.updateLightClientIfNeededTo(ctx, &res.Block.Height)
 	if err != nil {
 		return nil, err
 	}
@@ -330,7 +333,7 @@ func (c *Client) BlockByHash(ctx context.Context, hash []byte) (*ctypes.ResultBl
 	}
 
 	// Update the light client if we're behind.
-	l, err := c.updateLightClientIfNeededTo(ctx, res.Block.Height)
+	l, err := c.updateLightClientIfNeededTo(ctx, &res.Block.Height)
 	if err != nil {
 		return nil, err
 	}
@@ -371,7 +374,8 @@ func (c *Client) BlockResults(ctx context.Context, height *int64) (*ctypes.Resul
 	}
 
 	// Update the light client if we're behind.
-	trustedBlock, err := c.updateLightClientIfNeededTo(ctx, h+1)
+	nextHeight := h + 1
+	trustedBlock, err := c.updateLightClientIfNeededTo(ctx, &nextHeight)
 	if err != nil {
 		return nil, err
 	}
@@ -409,7 +413,8 @@ func (c *Client) BlockResults(ctx context.Context, height *int64) (*ctypes.Resul
 
 func (c *Client) Commit(ctx context.Context, height *int64) (*ctypes.ResultCommit, error) {
 	// Update the light client if we're behind and retrieve the light block at the requested height
-	l, err := c.updateLightClientIfNeededTo(ctx, *height)
+	// or at the latest height if no height is provided.
+	l, err := c.updateLightClientIfNeededTo(ctx, height)
 	if err != nil {
 		return nil, err
 	}
@@ -434,7 +439,7 @@ func (c *Client) Tx(ctx context.Context, hash []byte, prove bool) (*ctypes.Resul
 	}
 
 	// Update the light client if we're behind.
-	l, err := c.updateLightClientIfNeededTo(ctx, res.Height)
+	l, err := c.updateLightClientIfNeededTo(ctx, &res.Height)
 	if err != nil {
 		return nil, err
 	}
@@ -451,8 +456,9 @@ func (c *Client) TxSearch(ctx context.Context, query string, prove bool, page, p
 // Validators fetches and verifies validators.
 func (c *Client) Validators(ctx context.Context, height *int64, pagePtr, perPagePtr *int) (*ctypes.ResultValidators,
 	error) {
-	// Update the light client if we're behind and retrieve the light block at the requested height.
-	l, err := c.updateLightClientIfNeededTo(ctx, *height)
+	// Update the light client if we're behind and retrieve the light block at the requested height
+	// or at the latest height if no height is provided.
+	l, err := c.updateLightClientIfNeededTo(ctx, height)
 	if err != nil {
 		return nil, err
 	}
@@ -469,7 +475,7 @@ func (c *Client) Validators(ctx context.Context, height *int64, pagePtr, perPage
 	v := l.ValidatorSet.Validators[skipCount : skipCount+tmmath.MinInt(perPage, totalCount-skipCount)]
 
 	return &ctypes.ResultValidators{
-		BlockHeight: *height,
+		BlockHeight: l.Height,
 		Validators:  v,
 		Count:       len(v),
 		Total:       totalCount}, nil
@@ -492,8 +498,16 @@ func (c *Client) UnsubscribeAll(ctx context.Context, subscriber string) error {
 	return c.next.UnsubscribeAll(ctx, subscriber)
 }
 
-func (c *Client) updateLightClientIfNeededTo(ctx context.Context, height int64) (*types.LightBlock, error) {
-	l, err := c.lc.VerifyLightBlockAtHeight(ctx, height, time.Now())
+func (c *Client) updateLightClientIfNeededTo(ctx context.Context, height *int64) (*types.LightBlock, error) {
+	var (
+		l   *types.LightBlock
+		err error
+	)
+	if height == nil {
+		l, err = c.lc.Update(ctx, time.Now())
+	} else {
+		l, err = c.lc.VerifyLightBlockAtHeight(ctx, *height, time.Now())
+	}
 	if err != nil {
 		return nil, fmt.Errorf("failed to update light client to %d: %w", height, err)
 	}
```

### light/rpc/mocks/light_client.go
```diff
@@ -1,4 +1,4 @@
-// Code generated by mockery v2.3.0. DO NOT EDIT.
+// Code generated by mockery v0.0.0-dev. DO NOT EDIT.
 
 package mocks
 
@@ -54,6 +54,29 @@ func (_m *LightClient) TrustedLightBlock(height int64) (*types.LightBlock, error
 	return r0, r1
 }
 
+// Update provides a mock function with given fields: ctx, now
+func (_m *LightClient) Update(ctx context.Context, now time.Time) (*types.LightBlock, error) {
+	ret := _m.Called(ctx, now)
+
+	var r0 *types.LightBlock
+	if rf, ok := ret.Get(0).(func(context.Context, time.Time) *types.LightBlock); ok {
+		r0 = rf(ctx, now)
+	} else {
+		if ret.Get(0) != nil {
+			r0 = ret.Get(0).(*types.LightBlock)
+		}
+	}
+
+	var r1 error
+	if rf, ok := ret.Get(1).(func(context.Context, time.Time) error); ok {
+		r1 = rf(ctx, now)
+	} else {
+		r1 = ret.Error(1)
+	}
+
+	return r0, r1
+}
+
 // VerifyLightBlockAtHeight provides a mock function with given fields: ctx, height, now
 func (_m *LightClient) VerifyLightBlockAtHeight(ctx context.Context, height int64, now time.Time) (*types.LightBlock, error) {
 	ret := _m.Called(ctx, height, now)
```

### Title
Unvalidated Negative `offset` in GraphQL Pagination Causes Out-of-Bounds Slice Panic - (File: core/web/resolver/query.go)

### Summary
The GraphQL `chains` resolver (and related paginated resolvers) convert a client-supplied `offset` argument to an `int` without checking for negative values, then use it directly as a Go slice index. This mirrors the root cause of CVE-2017-17446, where `Mem_File_Reader::read_avail` failed to ensure a non-negative size before using it in a buffer read, causing a crash. Here, a negative `offset` is used directly in Go slice expressions such as `chains[offset:end]`, which triggers a runtime panic (`slice bounds out of range`) instead of a controlled error response.

### Finding Description
`pageOffset` simply casts the client-controlled `*int32` to `int` with no lower-bound check: [1](#0-0) 

The `Chains` resolver only validates the upper bound (`offset >= count`) but never checks `offset < 0` before slicing the results: [2](#0-1) 

The same unguarded `pageOffset`/`pageLimit` pattern feeds directly into `EthTransactions` / `EthTransactionsAttempts`, which pass the raw offset/limit to the transaction store: [3](#0-2) 

Downstream, `CoreRelayerChainInteroperators.ChainStatuses` and `NodeStatuses` also slice on `offset` (`stats[offset:offset+limit]`, `result[offset:]`) without validating that it is non-negative: [4](#0-3) 

In Go, slicing a slice with a negative index (e.g. `s[-1:]`) is a runtime panic, directly analogous to the C++ negative-size read that crashed `game-music-emu`: the code assumes a size/offset value is non-negative and never explicitly checks it before performing a bounds-sensitive memory operation.

### Impact Explanation
A client that can reach the GraphQL API (any authenticated node operator/API-token holder, regardless of the specific role granted) can pass a negative `offset` argument to trigger a panic in the resolver goroutine handling the request. Depending on whether the GraphQL/gin middleware stack recovers per-request panics, this results in, at minimum, an unhandled 500 error for that request, and in the worst case (if the panic is not recovered before reaching the top-level server loop) could crash or destabilize the node process — a denial-of-service condition consistent with the CVSS vector of the referenced CVE (`AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H`).

### Likelihood Explanation
Likelihood is high for triggering the panic condition itself, since it only requires supplying a negative integer to a pagination argument on a standard, documented GraphQL query (`chains`, `ethTransactions`, `ethTransactionsAttempts`) — no special privilege beyond a valid API session/token is required. Whether this escalates to an actual process crash depends on the presence/absence of panic-recovery middleware around the GraphQL handler, which could not be fully confirmed within the scope of this scan.

### Recommendation
Validate `offset` (and `limit`) for negativity immediately after conversion in `pageOffset`/`pageLimit` (and in `ParsePaginatedRequest`-style equivalents for GraphQL), returning a client error instead of proceeding. Apply the same explicit bounds checks (`offset < 0`, `offset > len(slice)`) before every slice expression in `Chains`, `ChainStatuses`, and `NodeStatuses` to fully eliminate the negative-index slicing path.

### Proof of Concept
Send a GraphQL query with a negative offset to an authenticated node API endpoint, e.g.:
```graphql
query {
  chains(offset: -1, limit: 10) {
    results { id }
  }
}
```
This reaches `Resolver.Chains`, which computes `offset := pageOffset(args.Offset)` = `-1`, passes the `offset >= count` upper-bound check (since `-1 < count`), and then executes `chains[offset:end]` i.e. `chains[-1:end]`, causing a runtime panic.

### Citations

**File:** core/web/resolver/helpers.go (L33-41)
```go
// pageOffset returns the default page offset if nil, otherwise it returns the
// provided offset.
func pageOffset(offset *int32) int {
	if offset == nil {
		return PageDefaultOffset
	}

	return int(*offset)
}
```

**File:** core/web/resolver/query.go (L116-158)
```go
func (r *Resolver) Chains(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*ChainsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	relayersMap := r.App.GetRelayers().GetIDToRelayerMap()

	chains := make([]chainlink.NetworkChainStatus, 0, len(relayersMap))
	for k, v := range relayersMap {
		s, err := v.GetChainStatus(ctx)
		if err != nil {
			return nil, err
		}

		chains = append(chains, chainlink.NetworkChainStatus{
			ChainStatus: s,
			Network:     k.Network,
		})
	}

	count := len(chains)
	if count == 0 {
		// No chains are configured, return an empty ChainsPayload, so we don't break the UI
		return NewChainsPayload(nil, 0), nil
	}

	// bound the chain results
	if offset >= count {
		return nil, fmt.Errorf("offset %d out of range", offset)
	}
	end := count
	if limit > 0 && offset+limit < end {
		end = offset + limit
	}

	sortByNetworkAndID(chains)
	return NewChainsPayload(chains[offset:end], safeInt32(count)), nil
```

**File:** core/web/resolver/query.go (L536-572)
```go
func (r *Resolver) EthTransactions(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*EthTransactionsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	txs, count, err := r.App.TxmStorageService().Transactions(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewEthTransactionsPayload(txs, safeInt32(count)), nil
}

func (r *Resolver) EthTransactionsAttempts(ctx context.Context, args struct {
	Offset *int32
	Limit  *int32
}) (*EthTransactionsAttemptsPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	offset := pageOffset(args.Offset)
	limit := pageLimit(args.Limit)

	attempts, count, err := r.App.TxmStorageService().TxAttempts(ctx, offset, limit)
	if err != nil {
		return nil, err
	}

	return NewEthTransactionsAttemptsPayload(attempts, safeInt32(count)), nil
}
```

**File:** core/services/chainlink/relayer_chain_interoperators.go (L334-367)
```go
func (rs *CoreRelayerChainInteroperators) ChainStatuses(ctx context.Context, offset, limit int) ([]NetworkChainStatus, int, error) {
	var (
		stats    []NetworkChainStatus
		totalErr error
	)
	rs.mu.Lock()
	defer rs.mu.Unlock()

	relayerIds := make([]types.RelayID, 0)
	for rid := range rs.loopRelayers {
		relayerIds = append(relayerIds, rid)
	}
	sort.Slice(relayerIds, func(i, j int) bool {
		return relayerIds[i].String() < relayerIds[j].String()
	})
	for _, rid := range relayerIds {
		lr := rs.loopRelayers[rid]
		stat, err := lr.GetChainStatus(ctx)
		if err != nil {
			totalErr = errors.Join(totalErr, err)
			continue
		}
		stats = append(stats, NetworkChainStatus{ChainStatus: stat, Network: rid.Network})
	}

	if totalErr != nil {
		return nil, 0, totalErr
	}
	cnt := len(stats)
	if len(stats) > limit+offset && limit > 0 {
		return stats[offset : offset+limit], cnt, nil
	}
	return stats[offset:], cnt, nil
}
```

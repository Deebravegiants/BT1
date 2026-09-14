Based on the investigation, the analog worth reporting is in the Feeds Manager RPC handler's `GetJobRuns` limit validation.

### Title
Missing negative/lower-bound validation of `GetJobRuns` limit parameter allows FMS to bypass pagination bound - (File: core/services/feeds/rpc_handlers.go)

### Summary
The `RPCHandlers.GetJobRuns` method, which processes requests from an external, network-connected Feeds Manager Service (FMS) over the wsrpc RPC channel, only validates the upper bound and zero-value case of the client-supplied `Limit` parameter, mirroring the class of bug in CL-2025-03 where a range/count request parameter was not fully validated before being used to drive a backing data query.

### Finding Description
`RPCHandlers.GetJobRuns` takes the `Limit` field directly from the untrusted, externally-supplied `pb.GetJobRunsRequest` and only special-cases two conditions: [1](#0-0) 
```
limit := req.Limit
...
if limit == 0 || limit > MaxJobRunsLimit {
    ...
    limit = DefaultJobRunsLimit
}
```
This check only clamps `limit` when it is exactly `0` or greater than `MaxJobRunsLimit` (100). Any negative value is neither `== 0` nor `> MaxJobRunsLimit`, so it passes through unchanged into `GetJobRunsArgs.Limit`, which is typed as `uint32`: [2](#0-1) 

That value is subsequently forwarded straight to `jobORM.PipelineRuns(ctx, &job.ID, 0, int(args.Limit))` inside `service.GetJobRuns`: [3](#0-2) 

This is structurally identical to the Teku bug: a range/count parameter taken from a remote peer/service is validated only against an upper bound / zero check, not for well-formedness (negative or overflowing values), before being used to drive a paginated backend query.

### Impact Explanation
Depending on how the request is marshaled over gRPC/wsrpc and how Go handles the negative-to-`uint32` conversion (`int64 -> uint32` truncation), a negative `Limit` supplied by the FMS could wrap around to a very large unsigned value (e.g., `-1` becomes `4294967295`), bypassing the intended `MaxJobRunsLimit = 100` cap entirely. This is passed as `int(args.Limit)` to the pipeline-runs query, which could force the ORM to attempt fetching an extremely large number of rows for a job, causing excessive database load / memory consumption — a resource-exhaustion (DoS) condition against the node, analogous to the unbounded range request in the reported Teku bug. The FMS connection is authenticated via CSA key exchange, but it is an external, remote-controlled service relative to node internals, so a malicious or compromised FMS endpoint could exploit this gap.

### Likelihood Explanation
Likelihood is moderate: exploitation requires a connected Feeds Manager (which is a trusted-but-external party per the node's configuration) to send a request with a negative `Limit`. It does not require breaking any cryptographic authentication — only a normal RPC call with a malformed field, since the wsrpc layer doesn't independently constrain field ranges. I could not fully verify the exact protobuf type of `pb.GetJobRunsRequest.Limit` in this index (whether it's declared as `int64`/`int32` allowing negative wire values, or `uint32`/`uint64` where negative values aren't representable) — this significantly affects exploitability and should be confirmed against the `chainlink-protos/orchestrator/feedsmanager` proto definitions, which were not found in this index.

### Recommendation
Add an explicit lower-bound check (`limit < 0`, if the underlying protobuf type permits negative values) or use an unsigned type at the protobuf layer, and validate the range with `limit <= 0 || limit > MaxJobRunsLimit` semantics computed safely without integer wraparound, before passing it into `GetJobRunsArgs.Limit` and onward to `PipelineRuns`.

### Proof of Concept
1. A connected Feeds Manager sends a `GetJobRuns` RPC with `Limit = -1` (or another negative value, if the wire type allows it).
2. In `RPCHandlers.GetJobRuns`, the check `limit == 0 || limit > MaxJobRunsLimit` evaluates false for negative values, so `limit` is not clamped.
3. `limit` is cast/assigned into `GetJobRunsArgs.Limit` (`uint32`), potentially wrapping to a very large number.
4. `service.GetJobRuns` calls `s.jobORM.PipelineRuns(ctx, &job.ID, 0, int(args.Limit))` with the huge/attacker-influenced limit value, causing an oversized query against the `pipeline_runs` table for that job. [1](#0-0) [3](#0-2)

### Citations

**File:** core/services/feeds/rpc_handlers.go (L90-104)
```go
// GetJobRuns fetches job run history for the specified job proposal
func (h *RPCHandlers) GetJobRuns(ctx context.Context, req *pb.GetJobRunsRequest) (*pb.GetJobRunsResponse, error) {
	remoteUUID, err := uuid.Parse(req.Id)
	limit := req.Limit
	if err != nil {
		return nil, fmt.Errorf("unable to parse request id (%s): %w", req.Id, err)
	}

	if limit == 0 || limit > MaxJobRunsLimit {
		h.lggr.Warnw("Invalid limit provided, using default",
			"requestedLimit", limit,
			"defaultLimit", DefaultJobRunsLimit,
		)
		limit = DefaultJobRunsLimit
	}
```

**File:** core/services/feeds/service.go (L589-594)
```go
// GetJobRunsArgs are the arguments to provide to the GetJobRuns method.
type GetJobRunsArgs struct {
	FeedsManagerID int64
	RemoteUUID     uuid.UUID
	Limit          uint32
}
```

**File:** core/services/feeds/service.go (L691-716)
```go
// GetJobRuns fetches recent job runs for a job by its remote UUID.
func (s *service) GetJobRuns(ctx context.Context, args *GetJobRunsArgs) ([]*pb.JobRunSummary, error) {
	s.lggr.Infow("FeedsService.GetJobRuns", "remoteUUID", args.RemoteUUID)

	job, err := s.jobORM.FindJobByExternalJobID(ctx, args.RemoteUUID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, fmt.Errorf("job not found: %w", err)
		}
		return nil, fmt.Errorf("failed to find job: %w", err)
	}

	isManagedByFM, err := s.orm.IsJobManagedByFeedsManager(ctx, int64(job.ID), args.FeedsManagerID)
	if err != nil {
		return nil, fmt.Errorf("failed to check if job is managed by feeds manager: %w", err)
	}

	if !isManagedByFM {
		return nil, errors.New("job is not managed by the requesting feeds manager")
	}

	runs, _, err := s.jobORM.PipelineRuns(ctx, &job.ID, 0, int(args.Limit))
	if err != nil {
		return nil, fmt.Errorf("failed to fetch job runs: %w", err)
	}

```

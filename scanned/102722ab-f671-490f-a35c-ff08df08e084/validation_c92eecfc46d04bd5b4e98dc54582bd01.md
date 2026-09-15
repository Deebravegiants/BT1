### Title
IDOR in Pipeline Run Show endpoint — any authenticated user can read any job's run history by run ID - ([File: core/web/pipeline_runs_controller.go])

### Summary
`PipelineRunsController.Show` in `core/web/pipeline_runs_controller.go` accepts a `runID` path parameter and fetches the corresponding pipeline run directly by primary key, with no check that the run belongs to the `:ID` (job) segment of the route, nor any check that the authenticated caller is authorized to view that specific job/run. This mirrors the Roxy-WI bug class: a path parameter is used directly as a record identifier with no per-resource authorization, letting any authenticated session enumerate another user's/job's run history.

### Finding Description
`Show` parses `runID` from the URL, loads it into a `pipeline.Run{}`, and calls: [1](#0-0) 

```go
func (prc *PipelineRunsController) Show(c *gin.Context) {
	ctx := c.Request.Context()
	pipelineRun := pipeline.Run{}
	err := pipelineRun.SetID(c.Param("runID"))
	...
	pipelineRun, err = prc.App.PipelineORM().FindRun(ctx, pipelineRun.ID)
	...
	res := presenters.NewPipelineRunResource(pipelineRun, prc.App.GetLogger())
	jsonAPIResponse(c, res, "pipelineRun")
}
```

`FindRun` performs an unscoped lookup by numeric ID with no job/owner filter: [2](#0-1) 

The route is reached via the standard authenticated router group (`authv2`), which only requires a valid session/token — it does not enforce that the caller has any relationship to the specific job whose run is being requested. Compare to `Index`, which at least scopes results by the job ID supplied in the path: [3](#0-2) 

`Show`, however, ignores the job/`:ID` context entirely and trusts `runID` as the sole selector, exactly the "path parameter reused as record identifier, no authorization check" pattern described in the Roxy-WI CVE.

### Impact Explanation
Pipeline runs contain job execution history: task inputs/outputs, bridge/adapter responses, error details, and other operational data tied to a specific job/job owner. Any authenticated Roxy-WI-analogous low-privilege user (e.g., a `view`-role Chainlink node operator user) can iterate `runID` values sequentially to read the full run history — including outputs and errors — of jobs they have no legitimate access to, resulting in unauthorized disclosure of another user's/job's operational data (cross-tenant/cross-user response confusion, IDOR-class, confidentiality impact only, matching CVSS C:L).

### Likelihood Explanation
Likelihood is high for any authenticated user of the node's HTTP API, since:
- `runID`s are sequential integers assigned by the DB, easy to enumerate.
- No additional authorization step is applied beyond basic session/token authentication (`auth.Authenticate`), unlike admin-only or edit-role-gated endpoints elsewhere in the router.
- No rate limiting or role differentiation is applied specifically to `Show`.

### Recommendation
Scope `Show` (and `FindRun`) to require the caller-provided job ID (`:ID`) match the run's associated job, and verify that job is one the authenticated user is authorized to view (e.g., in multi-tenant/enterprise-role deployments). At minimum, join/validate against `job_pipeline_specs`/`jobs` to ensure `runID` belongs to the `jobID` in the path, returning 404 on mismatch, and audit-log unauthorized access attempts as is already done for `Resume`.

### Proof of Concept
1. Authenticate as any valid user (even a `view`-role account with a session/API token).
2. Send `GET /v2/pipeline_runs/1`, `/v2/pipeline_runs/2`, ... incrementing `runID`.
3. Observe that the endpoint returns full run details (inputs, outputs, errors) for jobs the account never created or was never granted access to, since `Show` never checks run ownership against the job ID or session user.

### Citations

**File:** core/web/pipeline_runs_controller.go (L29-61)
```go
func (prc *PipelineRunsController) Index(c *gin.Context, size, page, offset int) {
	id := c.Param("ID")

	// Temporary: if no size is passed in, use a large page size. Remove once frontend can handle pagination
	if c.Query("size") == "" {
		size = 1000
	}

	var pipelineRuns []pipeline.Run
	var count int
	var err error

	ctx := c.Request.Context()
	if id == "" {
		pipelineRuns, count, err = prc.App.JobORM().PipelineRuns(ctx, nil, offset, size)
	} else {
		jobSpec := job.Job{}
		err = jobSpec.SetID(c.Param("ID"))
		if err != nil {
			jsonAPIError(c, http.StatusUnprocessableEntity, err)
			return
		}

		pipelineRuns, count, err = prc.App.JobORM().PipelineRuns(ctx, &jobSpec.ID, offset, size)
	}

	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	res := presenters.NewPipelineRunResources(pipelineRuns, prc.App.GetLogger())
	paginatedResponse(c, "pipelineRun", size, page, res, count, err)
```

**File:** core/web/pipeline_runs_controller.go (L67-84)
```go
func (prc *PipelineRunsController) Show(c *gin.Context) {
	ctx := c.Request.Context()
	pipelineRun := pipeline.Run{}
	err := pipelineRun.SetID(c.Param("runID"))
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	pipelineRun, err = prc.App.PipelineORM().FindRun(ctx, pipelineRun.ID)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	res := presenters.NewPipelineRunResource(pipelineRun, prc.App.GetLogger())
	jsonAPIResponse(c, res, "pipelineRun")
}
```

**File:** core/services/pipeline/orm.go (L516-528)
```go
func (o *orm) FindRun(ctx context.Context, id int64) (r Run, err error) {
	var runs []*Run
	err = o.transact(ctx, func(tx *orm) error {
		if err = tx.ds.SelectContext(ctx, &runs, `SELECT * from pipeline_runs WHERE id = $1 LIMIT 1`, id); err != nil {
			return errors.Wrap(err, "failed to load runs")
		}
		return loadAssociations(ctx, tx.ds, runs)
	})
	if len(runs) == 0 {
		return r, sql.ErrNoRows
	}
	return *runs[0], err
}
```

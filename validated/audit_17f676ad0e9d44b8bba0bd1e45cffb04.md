### Title
`PipelineRunsController.Show` returns pipeline run data for any `runID` without verifying it belongs to the `jobID` in the URL, or to the requesting user - ([File: core/web/pipeline_runs_controller.go])

### Summary
The `Show` handler for `GET /v2/jobs/:ID/runs/:runID` fetches a pipeline run purely by `runID`, ignoring the `:ID` (job ID) path parameter and any notion of run ownership, mirroring the reported analog bug class: an endpoint returns data for an arbitrary identifier without checking that the ID is valid/scoped to the caller's context, allowing an authenticated but unprivileged/low-role client to retrieve data that "appears genuine" for a resource it should not be allowed to view directly.

### Finding Description
`Show` parses only `runID` from the URL and calls `FindRun` directly: [1](#0-0) 

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

`FindRun` performs a plain lookup by primary key with no relationship to the `jobID` supplied in the same route (`/jobs/:ID/runs/:runID`), unlike `Index`, which correctly scopes results to `jobSpec.ID`: [2](#0-1) 

Compare this to `Index`, which filters `PipelineRuns(ctx, &jobSpec.ID, ...)` — i.e., scoped by job. `Show` has no equivalent check that the returned run's `PipelineSpecID`/job actually corresponds to the `:ID` in the path. Any authenticated node-API user with access to this route (any role that can hit `/v2/jobs/*/runs/*`) can enumerate/guess `runID` values across all jobs on the node and retrieve run details (inputs/outputs, task run results, potentially secrets echoed into pipeline outputs) belonging to jobs/pipelines they did not request through the intended job path — a cross-run/cross-job response confusion, analogous to `tokenURI()` returning data for an ID that was never validated against the calling context.

I could not fully verify from the available index what role gating (Admin/Edit/Run) applies specifically to this route in `router.go`, since the relevant route-registration lines for `runs/:runID` were not returned by the search tool before the iteration limit was reached. This is a limitation of the investigation, not a claim that all roles are unauthenticated.

### Impact Explanation
If any authenticated role weaker than the job's owner/admin can hit this route (e.g., a `Run`-level external-initiator-derived session, or any user with only `run` permissions used elsewhere in the codebase for webhook triggers), they could pull pipeline run results for unrelated jobs by iterating `runID`, exposing potentially sensitive computed values, task outputs, or error details from other jobs' runs. This is an information-disclosure / cross-user (cross-job) response confusion issue, directly analogous to the reported `tokenURI()`/`stakingInfo()` finding: the method does not check that the requested ID is the one the caller is authorized/expected to view in this context.

### Likelihood Explanation
Likelihood is moderate: `runID`s are sequential/integer primary keys (not UUIDs), making enumeration straightforward once a valid session/token is obtained. The main mitigating factor is that this route sits behind the node's HTTP session/token authentication (`AuthenticateByToken`/`AuthenticateBySession`), so exploitation requires some valid credential, but no additional per-run authorization check exists beyond that.

### Recommendation
In `Show`, after parsing `:ID` from the path, verify that the fetched `pipelineRun.PipelineSpecID`/job foreign key actually corresponds to the job identified by `:ID` (similar to how `Index` scopes by `jobSpec.ID`), and return `404 Not Found` if it does not match, mirroring the recommendation from the analog report to explicitly validate existence/ownership of the referenced resource before returning data.

### Proof of Concept
1. As an authenticated node-API user (any role permitted on `/v2/jobs/*/runs/*`), create/own Job A and note none of its run IDs.
2. Call `GET /v2/jobs/<jobA_ID>/runs/<runID_of_jobB>` where `runID_of_jobB` belongs to a different job (Job B) owned by another party.
3. Observe that `Show` returns Job B's pipeline run data (task outputs, errors, etc.) even though the URL path referenced Job A, because `FindRun` is only keyed on `runID` and never cross-checked against the job ID in the path.

### Citations

**File:** core/web/pipeline_runs_controller.go (L26-62)
```go
// Index returns all pipeline runs for a job.
// Example:
// "GET <application>/jobs/:ID/runs"
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
}
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

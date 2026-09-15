Based on my investigation, the `PipelineRunsController.Show` endpoint has a bug-class match to the CVE, but with limited practical impact given Chainlink's single-tenant node authorization model.

### Title
Job Run Show endpoint ignores job-scoping (`:ID`) and returns any run by `:runID` alone - (File: core/web/pipeline_runs_controller.go)

### Summary
The route `GET /v2/jobs/:ID/runs/:runID` is intended to fetch a pipeline run scoped to a specific job, but `PipelineRunsController.Show` never reads or validates the `:ID` path parameter — it only parses `:runID` and fetches the run directly by that ID.

### Finding Description
`Show` parses only `c.Param("runID")` into `pipelineRun.SetID`, then calls `prc.App.PipelineORM().FindRun(ctx, pipelineRun.ID)` without ever checking that the returned run's `JobID` matches the `:ID` from the URL path. [1](#0-0) 
This mirrors the CVE-2021-39234 bug class: a caller who knows/can enumerate an object ID (a run ID here, analogous to Ozone's block ID) can access it directly, bypassing the "scoping" check implied by the URL structure (`/jobs/:ID/runs/:runID`), because the handler silently ignores the outer scoping parameter.

The route is registered as: [2](#0-1) 
which is guarded only by generic session/token authentication (`authv2` group), with no per-job or per-run role/ACL check. [3](#0-2) 

### Impact Explanation
In the current single-tenant Chainlink node model, any authenticated user (even a "view"-only role) can already list all runs via `/v2/jobs/:ID/runs` or `/v2/pipeline/runs`, so runs are not considered private per-job or per-user resources within one node. Because there is no per-job ACL model in this codebase (unlike Ozone's block ACLs), the missing `:ID`/`:runID` cross-check does not bypass any access-control boundary that exists elsewhere — it's a scoping oversight, not a privilege escalation. This differs materially from the CVE's context (Ozone has per-key/per-block ACLs that are being bypassed).

### Likelihood Explanation
Trivial to trigger by any authenticated user, but only discloses data (run inputs/outputs) they could already view via the unscoped listing endpoints.

### Recommendation
For defense-in-depth and correctness, `Show` should validate that the fetched `pipelineRun`'s `JobID` matches the job specified by `:ID`, returning 404 if it does not, so that the URL's stated scoping is actually enforced.

### Proof of Concept
1. Authenticate as any valid user session/token.
2. Call `GET /v2/jobs/999999/runs/1` where `1` is a real run ID belonging to a different job.
3. Observe response 200 with the pipeline run data for run `1`, despite it not belonging to job `999999`.

**Caveat:** I could not find any per-job or per-user ACL enforced elsewhere in this codebase for job runs (all authenticated roles that can view jobs at all can view all runs via `/v2/pipeline/runs`), so this finding represents a minor scoping inconsistency rather than a genuine authorization bypass matching the severity of the source CVE. If the wiki/product intends job runs to be tenant/role-scoped in the future, this gap should be flagged for that design; as it stands today, it has no additional confirmed unauthorized-access impact beyond what's already exposed by design.

### Citations

**File:** core/web/pipeline_runs_controller.go (L64-84)
```go
// Show returns a specified pipeline run.
// Example:
// "GET <application>/jobs/:ID/runs/:runID"
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

**File:** core/web/router.go (L245-248)
```go
	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
```

**File:** core/web/router.go (L399-401)
```go
		authv2.GET("/pipeline/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs/:runID", prc.Show)
```

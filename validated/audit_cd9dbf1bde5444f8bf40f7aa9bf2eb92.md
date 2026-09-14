### Title
Improper access control in `PipelineRunsController.Show` allows any authenticated user to read arbitrary job-run data without ownership checks - (File: `core/web/pipeline_runs_controller.go`)

### Summary
`PipelineRunsController.Show`, mounted at `GET /v2/jobs/:ID/runs/:runID`, fetches a pipeline run purely by `runID` and returns its full contents without ever validating that the run belongs to the job identified by `:ID` in the path, and without any role check beyond generic session authentication.

### Finding Description
The route is registered in the `authv2` group with no additional role guard: [1](#0-0) 

Compare this to sibling routes in the same group that are explicitly wrapped with `auth.RequiresEditRole`/`auth.RequiresAdminRole` (e.g. job creation, key export/import), showing the codebase's own pattern of requiring elevated roles for sensitive reads/writes: [2](#0-1) 

The handler itself ignores the `:ID` job path parameter entirely and looks the run up solely from `:runID`: [3](#0-2) 

`FindRun` performs a lookup keyed purely on the numeric run ID with no ownership/job-scope predicate, so any authenticated caller (even the lowest privilege, "view", role — since `Show` is not wrapped by `RequiresEditRole`/`RequiresRunRole`/`RequiresAdminRole` like other endpoints) can retrieve the full presenter payload of a pipeline run belonging to any job in the node, simply by iterating `runID` values. This is directly analogous to the iTop `ajax.render.php`/`ajax.document.php` bug class: a document/resource-serving endpoint that trusts an opaque numeric identifier without an accompanying permission or ownership check tied to the caller.

### Impact Explanation
Pipeline run resources can contain sensitive execution data (task inputs/outputs, error details, and potentially secrets flowing through pipeline tasks depending on job configuration). A low-privileged (`view`-role) authenticated user can enumerate `runID`s and read run details for jobs they should have no visibility into, resulting in unauthorized information disclosure / cross-user response confusion, matching the CVSS vector for the analog (`C:H`, `PR:L`).

### Likelihood Explanation
Any authenticated node API user, regardless of assigned role, can reach this endpoint since it lacks a `RequiresXRole` wrapper; only sequential/guessable integer `runID`s are required, making exploitation straightforward for any user who already holds any valid session/API token on the node.

### Recommendation
Add an explicit role gate (at minimum `auth.RequiresRunRole` matching other run-triggering endpoints) and, more importantly, validate that the fetched run's `job_id` matches the `:ID` path parameter (or otherwise scope `FindRun` by an authorization-checked job/owner filter) before returning the presenter response in `PipelineRunsController.Show`.

### Proof of Concept
1. Authenticate as a low-privileged (`view`-role) node API user.
2. Send `GET /v2/jobs/<any-id>/runs/<runID>` while incrementing `runID` sequentially.
3. Observe that the response returns full pipeline run details for runs belonging to jobs the user has no legitimate access to, since neither the route registration (`core/web/router.go:401`) nor the handler (`core/web/pipeline_runs_controller.go:67-84`) verify that the run belongs to the specified job or that the caller is authorized for that job.

### Citations

**File:** core/web/router.go (L391-396)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
```

**File:** core/web/router.go (L398-401)
```go
		// PipelineRunsController
		authv2.GET("/pipeline/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs", paginatedRequest(prc.Index))
		authv2.GET("/jobs/:ID/runs/:runID", prc.Show)
```

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

## Finding: External Initiator authentication grants a broad "Run" role instead of a job-scoped permission, enabling any external initiator to trigger any job on the node

### Title
Over-privileged External Initiator authentication enables unauthorized triggering of arbitrary jobs - (File: core/web/auth/auth.go)

### Summary
This maps to the reported bug class: an actor meant to hold narrow, single-purpose privileges is instead granted broad node-wide capability. In the Gearbox report, the Configurator role (meant only to tune specific risk parameters) could move all user funds. In this codebase, an External Initiator (EA) — a credential meant to let one specific webhook/bridge trigger runs of the job it was created for — is instead granted the generic, node-wide `UserRoleRun` role, and the run-creation route accepts an arbitrary job ID with no check that the authenticated initiator is actually associated with that job.

### Finding Description
When a request authenticates via `AuthenticateExternalInitiator`, the middleware unconditionally sets a full `run`-role user in the context, with no binding to which job/bridge that specific initiator is permitted to trigger: [1](#0-0) 

That role is exactly the role gate used on the job-run creation endpoint, which is reachable by any of external-initiator, token, or session auth and accepts an arbitrary `:ID` path parameter for the target job: [2](#0-1) 

Because `RequiresRunRole` only checks the coarse-grained role (not a per-job scope) — mirroring the same admin/edit/run/view coarse role checks used everywhere else in `core/web/auth/auth.go` — [3](#0-2)  — an External Initiator record created for job/bridge "A" is authenticated with the same generic `run` role as any other run-capable credential, and the route layer does not verify that the specific `ExternalInitiator` (`ei` set via `SessionExternalInitiatorKey`) is the one associated with job `ID` before calling `prc.Create`.

This is structurally the same class of issue as the reported "Configurator has too many rights": a credential intended to be scoped narrowly (Configurator → specific risk parameters; External Initiator → its own webhook job) is instead granted broad, node-wide capability (Configurator → drain any user's collateral; External Initiator → trigger any job on the node).

### Impact Explanation
An unprivileged external actor holding only one external-initiator's access key/secret (e.g., leaked from one integrated third-party bridge) can call `POST /v2/jobs/:ID/runs` for any job ID configured on the node, not just the job tied to their own initiator. Depending on what other jobs exist on the node (e.g., jobs that move funds, submit transactions, or perform sensitive on-chain actions via `ethtx`/`vrf`/`keeper` pipelines), this could result in unauthorized job execution and downstream unauthorized fund movement or state changes, without needing any `edit`/`admin` credential.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that uses multiple external initiators and/or has webhook-triggered jobs performing privileged actions: only a single leaked/compromised EA access key + secret pair is needed (no admin/edit access required), and the vulnerable endpoint is reachable directly from a standard authenticated HTTP request with no additional per-job authorization check visible in the routing/middleware layer.

### Recommendation
Bind External Initiator authentication to the specific job(s)/bridge it was created for, and enforce that binding in `PipelineRunsController.Create` (or an equivalent scoping check before `RequiresRunRole` is satisfied) rather than granting a blanket run-role that applies to every job ID. Concretely: look up the job's associated external initiator/bridge from the `:ID` path param and reject the request (403) if `SessionExternalInitiatorKey` does not match the job's own configured initiator.

### Proof of Concept
1. Create two webhook-triggered jobs, Job A and Job B, each intended to be triggered by its own separate External Initiator (`POST /v2/external_initiators`).
2. Obtain the access key/secret for the External Initiator tied to Job A only.
3. Send `POST /v2/jobs/<JobB-ID>/runs` with headers `X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret` set to Job A's initiator credentials.
4. Observe the request succeeds (route only checks `RequiresRunRole`, satisfied by any valid EA auth) and triggers a run of Job B, which the caller's credential was never provisioned for.

**Note on verification limits:** I could not fully inspect the internal body of `PipelineRunsController.Create` (`core/web/pipeline_runs_controller.go`) in this session to confirm there is no additional job-to-initiator ownership check performed inside the handler itself before creating the run; the analysis above is based on the authentication middleware (`core/web/auth/auth.go`) and routing (`core/web/router.go`), which show no such scoping at the role-gate level. If a job-ownership check does exist inside the controller body, the practical exploitability would be reduced accordingly — this should be confirmed with a full read of that controller before treating this as fully confirmed.

### Citations

**File:** core/web/auth/auth.go (L143-149)
```go
	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```

**File:** core/web/auth/auth.go (L215-234)
```go
}

// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/router.go (L449-456)
```go
	ping := PingController{app}
	userOrEI := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateExternalInitiator,
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	userOrEI.GET("/ping", ping.Show)
	userOrEI.POST("/jobs/:ID/runs", auth.RequiresRunRole(prc.Create))
```

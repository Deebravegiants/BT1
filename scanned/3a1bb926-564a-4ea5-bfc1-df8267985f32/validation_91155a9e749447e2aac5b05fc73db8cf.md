### Title
Job configuration API exposes unmasked pipeline/task secrets to view-only users - ([File: core/web/presenters/job.go])

### Summary
Chainlink job specs' `DotDagSource` (the raw pipeline TOML/DAG definition submitted by an edit-role user) is returned verbatim, with no redaction, by the `GET /v2/jobs` and `GET /v2/jobs/:ID` endpoints. These read endpoints require only an authenticated session with the minimal `view` role, not the `edit`/`run`/`admin` roles that are required to create or mutate jobs. Pipeline tasks such as `http` commonly embed secrets (API keys, bearer tokens, custom headers, or request bodies) directly in the task parameters as literal strings, since Chainlink pipeline DSL has no first-class "secret" type distinct from a plain string. This mirrors the Jenkins Ansible plugin issue: a job configuration mechanism that allows/encourages embedding secrets as plain configuration values, which are then displayed unmasked to any principal with read access to the job.

### Finding Description
`JobsController.Show` and `JobsController.Index` (`core/web/jobs_controller.go:44-90`) build a `presenters.JobResource` from the stored `job.Job` and return it via `jsonAPIResponse`/`paginatedResponse`. The presenter unconditionally copies the full pipeline definition: [1](#0-0) 

into the `pipelineSpec.dotDagSource` field of the JSON response: [2](#0-1) 

No redaction, masking, or stripping of embedded secret-like values (e.g., HTTP task headers, API keys in URLs, or request bodies) is performed anywhere in this path.

Crucially, these read routes are registered without any elevated-role middleware, unlike the mutating routes: [3](#0-2) 

This is confirmed by the RBAC route matrix used in tests, where `GET /v2/jobs` and `GET /v2/jobs/MOCK` are marked `viewOnlyAllowed: true`, while `POST`/`PUT`/`DELETE` require edit role: [4](#0-3) 

So any authenticated user provisioned with the lowest privilege level (`UserRoleView`) can call `GET /v2/jobs/:ID` and receive the complete, unmasked pipeline source of every job — including any secrets an operator embedded in `http`/`bridge` task parameters (headers, query strings, request bodies) when authoring the job.

This is directly analogous to the reported Jenkins Ansible Plugin issue: Jenkins allowed "extra variables," commonly used to pass secrets, to be stored unencrypted and displayed unmasked to users with a lesser permission (`Item/Extended Read`) than the one required to configure the job. Here, Chainlink's job pipeline DSL similarly allows arbitrary secret-bearing strings to be embedded as configuration ("http" task headers/URLs/body), and the read API design intentionally permits `view`-role users — who cannot create or edit jobs — to fetch this data unmasked.

### Impact Explanation
Any user provisioned with the `view` role (lowest privilege tier, intended for read-only dashboards/monitoring) can retrieve the full pipeline definitions of all jobs on the node, including any credentials/secrets an operator embedded directly in pipeline task parameters (e.g., external adapter API keys, custom `Authorization` headers, webhook tokens embedded in URLs). This is a confidentiality violation (CWE-312: cleartext storage of sensitive information, exposed via API) consistent with the CVSS profile of the referenced advisory (`C:L`), since it requires an authenticated but low-privileged principal and yields disclosure of credentials without directly enabling code execution or job mutation. The severity depends on operational practice — nodes where operators embed secrets directly into pipeline task strings (rather than referencing bridge-stored tokens) are directly exposed.

### Likelihood Explanation
Likelihood is moderate: exploitation requires (1) an attacker/insider to hold a valid `view`-role session (which node operators may hand out broadly for read-only monitoring/audit purposes, believing it to be low-risk), and (2) at least one job on the node embedding a secret directly in its pipeline definition rather than via the dedicated bridge-secret mechanism. Chainlink does provide the bridge mechanism (`core/bridges/bridge_type.go`) specifically to avoid embedding secrets in job specs, but nothing prevents operators from putting raw secrets into `http` task parameters, and the API/documentation gives no warning or masking behavior comparable to what Jenkins added in its fix.

### Recommendation
- Redact known-sensitive substrings/patterns (e.g., `Authorization`, `apikey`, bearer tokens) from `DotDagSource` before returning it through `presenters.NewPipelineSpec`, or provide a masked view by default and an explicit elevated-role-gated endpoint for the raw definition.
- Restrict `GET /v2/jobs` and `GET /v2/jobs/:ID` (and the GraphQL `job`/`jobs` resolvers) to require at least the `run` or `edit` role rather than `view`, consistent with how Jenkins scoped the fix to require elevated (`Item/Extended Read`) permission and then still added masking on top.
- Document and enforce that secrets must only be referenced via bridge tokens or the secrets-store mechanisms, never embedded literally in pipeline task strings, and add spec validation that flags common secret patterns in `observationSource`.

### Proof of Concept
1. As an admin, create a user with `UserRoleView` (`POST /v2/users`, role `view`).
2. As an edit-role/admin user, create a job whose pipeline includes a secret directly, e.g.:
   ```
   fetch [type=http method=GET url="https://api.example.com/data" headers="Authorization: Bearer SUPER_SECRET_TOKEN"];
   ```
   via `POST /v2/jobs` (`core/web/jobs_controller.go:101-134`).
3. Authenticate as the `view`-role user and call `GET /v2/jobs/:ID`.
4. Observe the response's `data.attributes.pipelineSpec.dotDagSource` contains the full, unredacted pipeline string including `Authorization: Bearer SUPER_SECRET_TOKEN`, confirmed by the presenter logic at `core/web/presenters/job.go:208-222` and the unrestricted GET route registration at `core/web/router.go:391-393`.

### Citations

**File:** core/web/presenters/job.go (L208-222)
```go
// PipelineSpec defines the spec details of the pipeline
type PipelineSpec struct {
	ID           int32  `json:"id"`
	JobID        int32  `json:"jobID"`
	DotDAGSource string `json:"dotDagSource"`
}

// NewPipelineSpec generates a new PipelineSpec from a pipeline.Spec
func NewPipelineSpec(spec *pipeline.Spec) PipelineSpec {
	return PipelineSpec{
		ID:           spec.ID,
		JobID:        spec.JobID,
		DotDAGSource: spec.DotDagSource,
	}
}
```

**File:** core/web/presenters/job.go (L539-569)
```go
// JobResource represents a JobResource
type JobResource struct {
	JAID
	Name                     string                    `json:"name"`
	StreamID                 *uint32                   `json:"streamID,omitempty"`
	Type                     JobSpecType               `json:"type"`
	SchemaVersion            uint32                    `json:"schemaVersion"`
	GasLimit                 clnull.Uint32             `json:"gasLimit"`
	ForwardingAllowed        bool                      `json:"forwardingAllowed"`
	MaxTaskDuration          sqlutil.Interval          `json:"maxTaskDuration"`
	ExternalJobID            uuid.UUID                 `json:"externalJobID"`
	DirectRequestSpec        *DirectRequestSpec        `json:"directRequestSpec"`
	FluxMonitorSpec          *FluxMonitorSpec          `json:"fluxMonitorSpec"`
	CRESettings              *CRESettingsSpec          `json:"creSettingsSpec"`
	CronSpec                 *CronSpec                 `json:"cronSpec"`
	OffChainReportingSpec    *OffChainReportingSpec    `json:"offChainReportingOracleSpec"`
	OffChainReporting2Spec   *OffChainReporting2Spec   `json:"offChainReporting2OracleSpec"`
	VRFSpec                  *VRFSpec                  `json:"vrfSpec"`
	WebhookSpec              *WebhookSpec              `json:"webhookSpec"`
	BlockhashStoreSpec       *BlockhashStoreSpec       `json:"blockhashStoreSpec"`
	BlockHeaderFeederSpec    *BlockHeaderFeederSpec    `json:"blockHeaderFeederSpec"`
	BootstrapSpec            *BootstrapSpec            `json:"bootstrapSpec"`
	GatewaySpec              *GatewaySpec              `json:"gatewaySpec"`
	WorkflowSpec             *WorkflowSpec             `json:"workflowSpec"`
	StandardCapabilitiesSpec *StandardCapabilitiesSpec `json:"standardCapabilitiesSpec"`
	CCIPSpec                 *CCIPSpec                 `json:"ccipSpec"`
	CCVCommitteeVerifierSpec *CCVCommitteeVerifierSpec `json:"ccvCommitteeVerifierSpec"`
	CCVExecutorSpec          *CCVExecutorSpec          `json:"ccvExecutorSpec"`
	PipelineSpec             PipelineSpec              `json:"pipelineSpec"`
	Errors                   []JobError                `json:"errors"`
}
```

**File:** core/web/router.go (L391-396)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
```

**File:** core/web/auth/auth_test.go (L309-312)
```go
	{"GET", "/v2/jobs", true, true, true},
	{"GET", "/v2/jobs/MOCK", true, true, true},
	{"POST", "/v2/jobs", false, false, true},
	{"DELETE", "/v2/jobs/MOCK", false, false, true},
```

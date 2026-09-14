## Title
Job telemetry emits full job spec (including embedded Mercury/plugin credentials) unredacted to Beholder - (File: `core/services/nodestatusreporter/jobspec/cl_job_info.go`)

### Summary
The Jenkins advisory concerns a secret being written unencrypted into a job's `config.xml`, readable by anyone with Extended Read permission on that job. The closest analog in this codebase is `JobSpecReporter`/`BuildCLJobInfo`, which TOML-serializes the *entire* `job.Job` struct — including type-specific specs such as `OCR2OracleSpec.RelayConfig`/`PluginConfig`, `VRFSpec`, `StreamSpec`, etc. — and ships it as unredacted telemetry to Beholder on every job create/delete/heartbeat event, without going through the same secret-redaction path used for node `Secrets` (`(*Secrets).TOMLString()`).

### Finding Description
`jobTOML` in `core/services/nodestatusreporter/jobspec/cl_job_info.go` does a raw `toml.Marshal(jb)` over the whole `job.Job` struct: [1](#0-0) 

This is invoked from `BuildCLJobInfo`, which is called unconditionally (no feature-flag/opt-in) on every job start, stop, and heartbeat poll via `JobSpecReporter`: [2](#0-1) [3](#0-2) 

The comment in `start()` explicitly notes this track "needs no per-node opt-in," unlike the legacy `JobSpecEvent` gated by `JobSpecReporter.Enabled`: [4](#0-3) 

By contrast, node-level `Secrets` (Database URL, OIDC client secret, Mercury credentials, etc.) go through a dedicated `TOMLString()` that leverages `config.SecretString`/`SecretURL` wrapper types to redact as `"xxxxx"` before ever being displayed or logged: [5](#0-4) [6](#0-5) 

`job.Job` and its specs have no equivalent redaction wrapper — fields like `OCR2OracleSpec.RelayConfig`/`PluginConfig` (arbitrary `map[string]any`/JSON blobs that plugin authors can and do use to carry credentials or API keys for external data sources) are passed through `toml.Marshal` verbatim: [7](#0-6) 

The test suite even documents this as intentional, generic behavior ("Load-bearing: an arbitrary job must round-trip to TOML with no per-type code"), confirming no field is excluded or masked regardless of sensitivity: [8](#0-7) 

### Impact Explanation
Any secret an operator embeds inside a job spec's `pluginConfig`/`relayConfig`/observation-source (e.g., a Mercury/data-source API key, or credentials passed to a custom bridge/adapter) is exported in cleartext, permanently, to the Beholder telemetry backend on every job lifecycle event and periodic heartbeat. This widens the exposure surface for that secret from "readable by node operators with DB/API access" to "readable by anyone with access to the telemetry pipeline/observability backend" — a materially different (and typically broader) set of consumers, directly mirroring the Jenkins CWE-256/CWE-522 pattern of a secret being persisted unencrypted somewhere accessible to non-owning parties.

### Likelihood Explanation
This triggers automatically and continuously (create, delete, and heartbeat poll of every active job) with no per-node opt-in, so likelihood of exposure is high wherever Beholder is enabled and any job spec contains sensitive values in its plugin/relay config or observation source. It requires no attacker action — it's a systemic overexposure ("no-impact-to-attacker-required" leak) rather than something requiring privilege escalation to trigger.

### Recommendation
Apply the same redaction discipline used for node `Secrets` to job-spec telemetry: introduce a redacting marshal path (or reuse `config.SecretString`-style wrapper types) for known-sensitive sub-fields of specs (`RelayConfig`, `PluginConfig`, credential-bearing task params in `Pipeline`/`ObservationSource`), or strip/allowlist only non-sensitive fields before calling `jobTOML`, rather than serializing the entire `job.Job` unmodified.

### Proof of Concept
1. Create an OCR2 job whose `pluginConfig` or `relayConfig` embeds a credential value (e.g., a Data Streams API key used by a custom adapter), submitted via `POST /v2/jobs` (`core/web/jobs_controller.go` `Create`).
2. Start the node with Beholder enabled (`JobSpecReporter` is unconditionally active).
3. Observe the `CLJobInfo.SpecToml` telemetry payload emitted on job start/heartbeat — the embedded credential appears in plaintext, as shown by the round-trip test asserting the full spec content is preserved verbatim (`TestBuildCLJobInfo_EncodesFullSpecAsTOML`).

**Caveat:** I could not confirm from the indexed code exactly which built-in job types place raw secret material into `RelayConfig`/`PluginConfig` at the schema level (this is largely at the discretion of operators/plugin authors via free-form JSON/TOML), so the concrete "credential in pluginConfig" scenario is inferred from the field's `map[string]any` type rather than a specific first-party secret field in `job.Job`. If you need a definitive list of which spec fields have historically carried secrets, a Devin session with full repo/grep access would be needed to check plugin-side config schemas (e.g., Mercury/Data Streams relayer config) that aren't fully indexed here.

### Citations

**File:** core/services/nodestatusreporter/jobspec/cl_job_info.go (L104-112)
```go
// jobTOML serializes the whole job.Job, which captures both the common fields
// and the single active type-specific spec.
func jobTOML(jb job.Job) (string, error) {
	out, err := toml.Marshal(jb)
	if err != nil {
		return "", err
	}
	return string(out), nil
}
```

**File:** core/services/nodestatusreporter/jobspec/job_spec_reporter.go (L73-84)
```go
// start always runs so CLJobInfo needs no per-node opt-in; the legacy track
// stays behind JobSpecReporter.Enabled (see ShouldEmit). Still a no-op where
// Beholder is disabled, which is the default.
func (s *Service) start(ctx context.Context) error {
	s.eng.Infow("Starting Job Spec Reporter Service",
		"clJobInfo", true, "legacyJobSpecEvent", s.config.Enabled())
	s.spawner.RegisterListener(s)
	ticker := services.NewTicker(s.config.PollingInterval())
	s.eng.GoTick(ticker, s.pollAllJobs)

	return nil
}
```

**File:** core/services/nodestatusreporter/jobspec/job_spec_reporter.go (L90-119)
```go
// AfterJobStarted emits a create event when a job starts.
func (s *Service) AfterJobStarted(ctx context.Context, jb job.Job) {
	s.emit(ctx, jb, commonv1.CLJobInfoTrigger_CL_JOB_INFO_TRIGGER_CREATE, events.EmissionTrigger_EMISSION_TRIGGER_CREATE)
}

// AfterJobStopped emits a delete event when a job is removed.
func (s *Service) AfterJobStopped(ctx context.Context, jb job.Job) {
	s.emit(ctx, jb, commonv1.CLJobInfoTrigger_CL_JOB_INFO_TRIGGER_DELETE, events.EmissionTrigger_EMISSION_TRIGGER_DELETE)
}

// pollAllJobs emits heartbeat telemetry for every active job.
func (s *Service) pollAllJobs(ctx context.Context) {
	for _, jb := range s.spawner.ActiveJobs() {
		s.emit(ctx, jb, commonv1.CLJobInfoTrigger_CL_JOB_INFO_TRIGGER_HEARTBEAT, events.EmissionTrigger_EMISSION_TRIGGER_HEARTBEAT)
	}
}

// emit reports jb on both tracks; a failure on one never suppresses the other.
func (s *Service) emit(ctx context.Context, jb job.Job, clTrigger commonv1.CLJobInfoTrigger, trigger events.EmissionTrigger) {
	if err := s.EmitCLJobInfoForJob(ctx, jb, clTrigger); err != nil {
		s.eng.Warnw("Failed to emit CLJobInfo", "jobID", jb.ID, "trigger", clTrigger, "error", err)
	}

	if !s.ShouldEmit(&jb) {
		return
	}
	if err := s.EmitForJob(ctx, jb, trigger); err != nil {
		s.eng.Warnw("Failed to emit job spec telemetry", "jobID", jb.ID, "trigger", trigger, "error", err)
	}
}
```

**File:** core/services/nodestatusreporter/jobspec/job_spec_reporter.go (L121-139)
```go
// EmitCLJobInfoForJob emits the generic CLJobInfo for any job type. A job whose
// spec won't TOML-encode is still reported without spec_toml, and the encoding
// error returned for logging.
func (s *Service) EmitCLJobInfoForJob(ctx context.Context, jb job.Job, trigger commonv1.CLJobInfoTrigger) error {
	prop, err := s.jobProposal(ctx, jb)
	if err != nil {
		// Provenance is an enrichment, not a precondition.
		s.eng.Warnw("Failed to resolve job proposal provenance for CLJobInfo",
			"jobID", jb.ID, "externalJobID", jb.ExternalJobID, "error", err)
	}

	identity := NodeIdentity{CSAPublicKey: s.csaPublicKey, NodeVersion: s.nodeVersion, Hostname: s.hostname}
	info, buildErr := BuildCLJobInfo(jb, trigger, identity, prop, time.Now())

	if emitErr := EmitCLJobInfo(ctx, s.emitter, info); emitErr != nil {
		return emitErr
	}
	return buildErr
}
```

**File:** core/services/chainlink/config.go (L448-455)
```go
// TOMLString returns a TOML encoded string with secret values redacted.
func (s *Secrets) TOMLString() (string, error) {
	b, err := gotoml.Marshal(s)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
```

**File:** core/store/models/secrets.go (L7-12)
```go
// Secret is a string that formats and encodes redacted, as "xxxxx".
// Deprecated
type Secret = config.SecretString

// Deprecated
func NewSecret(s string) *Secret { return config.NewSecretString(s) }
```

**File:** core/services/nodestatusreporter/jobspec/cl_job_info_test.go (L33-43)
```go
		OCR2OracleSpec: &job.OCR2OracleSpec{
			Relay:         "evm",
			ChainID:       "1",
			PluginType:    commontypes.Median,
			ContractID:    "0xcccccccccccccccccccccccccccccccccccccccc",
			TransmitterID: null.StringFrom("0x1111111111111111111111111111111111111111"),
			RelayConfig: job.JSONConfig{
				"chainID":     "1",
				"sendingKeys": []any{"0x1111111111111111111111111111111111111111"},
			},
		},
```

**File:** core/services/nodestatusreporter/jobspec/cl_job_info_test.go (L50-56)
```go
// Load-bearing: an arbitrary job must round-trip to TOML with no per-type code.
func TestBuildCLJobInfo_EncodesFullSpecAsTOML(t *testing.T) {
	t.Parallel()
	jb := clJobInfoSampleJob()
	id := jobspec.NodeIdentity{CSAPublicKey: "csa", NodeVersion: "1.2.3", Hostname: "host-1"}

	info, err := jobspec.BuildCLJobInfo(jb, commonv1.CLJobInfoTrigger_CL_JOB_INFO_TRIGGER_CREATE, id, nil, time.Date(2026, 7, 24, 12, 0, 0, 0, time.UTC))
```

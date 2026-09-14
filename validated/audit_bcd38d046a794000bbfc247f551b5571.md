Based on the investigation, I found a strong analog in the chainlink codebase for the reNgine command-injection pattern.

### Title
Command Execution via Standard Capabilities Job Spec `command` Field with Only Edit-Role Authorization - (File: `core/services/standardcapabilities/delegate.go`, `plugins/cmd.go`)

### Summary
reNgine's CVE-2024-58287 lets an authenticated user modify a scan-engine config parameter (`nmap_cmd`) that is later passed unchecked to a shell command. The chainlink analog is the `StandardCapabilities` job type's `command` field: any user holding only the "Edit" role (not "Admin") can submit a job spec TOML whose `command` string is later fed directly into `os/exec.Command` with no allowlist validation, executing an arbitrary binary/path on the node's host.

### Finding Description
`CreateJob` in the GraphQL resolver only requires `authenticateUserCanEdit`, i.e., Edit role is sufficient — not Admin: [1](#0-0) 

For `job.StandardCapabilities` type, the TOML is parsed by `ValidatedStandardCapabilitiesSpec`, which only checks that `Command` is non-empty — it does not validate the value against any allowlist of known binaries or paths: [2](#0-1) 

The same relaxed validation applies to the equivalent REST endpoint `POST /v2/jobs`, gated by `auth.RequiresEditRole`: [3](#0-2) [4](#0-3) 

When the job is scheduled, `Delegate.ServicesForSpec` extracts `command` straight from the job spec and threads it to `NewServices` → `NewStandardCapabilities`: [5](#0-4) 

`StandardCapabilities.Start` passes that raw string to `RegisterLOOP`/`NewCmdFactory`: [6](#0-5) 

Which finally executes it with `exec.Command`, explicitly suppressing the gosec warning about attacker-controlled command values ("we control the value of the cmd" — an assumption that doesn't hold once an Edit-role user can set it): [7](#0-6) 

The only mitigating check — `IsAllowlisted` via `RegistryBasedLaunchAllowlist` — is a deny-list for capabilities that are *already* registered on-chain; capabilities/binaries not in that map (including arbitrary local paths) bypass it entirely, as shown by the "unknown command bypasses allowlist check" test case: [8](#0-7) 

### Impact Explanation
An Edit-role user (a lower-privilege authenticated role, distinct from Admin) can create/update a `standardcapabilities` job spec with `command` set to any path/binary reachable by the node process (e.g., `/bin/sh` with crafted args via a wrapper script, or any pre-planted executable), achieving arbitrary code execution on the chainlink node host under the node's process privileges. This can lead to full node compromise, key/secret exfiltration (CSA/OCR/EVM keys held by the node), and fund movement if EVM signing keys are accessible.

### Likelihood Explanation
Requires only an authenticated user with Edit role (not Admin) — a role explicitly intended to be less privileged and is commonly granted to operators for day-to-day job management. No additional network position or code review gate is needed; a single `CreateJob`/`POST /v2/jobs` call is sufficient once the spec passes minimal TOML validation.

### Recommendation
Require Admin role for creating/updating `StandardCapabilities` (and other LOOP-launching) job specs, or introduce a strict allowlist of permitted `command` binaries/paths validated in `ValidatedStandardCapabilitiesSpec` before the value is ever passed into `exec.Command`. Additionally, resolve/canonicalize the path and reject values outside a trusted capabilities directory (mirroring the `DefaultCapabilitiesDir` restriction seen in test tooling) rather than trusting the raw operator-supplied string.

### Proof of Concept
1. Authenticate as a user with role `Edit` (not `Admin`).
2. Call the GraphQL `createJob` mutation (or `POST /v2/jobs`) with TOML:
   ```
   type = "standardcapabilities"
   schemaVersion = 1
   name = "poc"
   externalJobID = "<uuid>"
   forwardingAllowed = false
   command = "/tmp/malicious-binary"
   config = """{}"""
   ```
3. `ValidatedStandardCapabilitiesSpec` accepts it since `Command` is non-empty and Oracle Factory is disabled.
4. Once scheduled, `Delegate.ServicesForSpec` → `NewStandardCapabilities` → `Start` → `RegisterLOOP` → `NewCmdFactory` invokes `exec.Command("/tmp/malicious-binary")` on the node host, executing attacker-supplied code.

### Citations

**File:** core/web/resolver/mutation.go (L1061-1068)
```go
func (r *Resolver) CreateJob(ctx context.Context, args struct {
	Input struct {
		TOML string
	}
}) (*CreateJobPayloadResolver, error) {
	if err := authenticateUserCanEdit(ctx); err != nil {
		return nil, err
	}
```

**File:** core/services/standardcapabilities/delegate.go (L143-167)
```go
func (d *Delegate) ServicesForSpec(ctx context.Context, spec job.Job) ([]job.ServiceCtx, error) {
	command := spec.StandardCapabilitiesSpec.Command
	configJSON := spec.StandardCapabilitiesSpec.Config

	if d.localCfg != nil {
		capabilityID := conversions.GetCapabilityIDFromCommand(command, configJSON)
		if capabilityID != "" && d.localCfg.IsAllowlisted(capabilityID) {
			return nil, fmt.Errorf(
				"capability %q is in the RegistryBasedLaunchAllowlist and will be started from the on-chain registry; "+
					"remove the job spec and let the LocalCapabilityManager handle it via [Capabilities.Local] TOML config",
				capabilityID,
			)
		}
	}

	// Job-spec boot path: capability DON ID is not carried in the spec, so the
	// host best-effort resolves it from the capability registry inside NewServices.
	// On a node that belongs to multiple DONs running the same capability, the
	// registry lookup cannot disambiguate which DON this plugin serves, so it
	// resolves to 0 and the plugin falls back to the consumer workflow's DON ID
	// for event labeling. Carrying the DON ID in the job spec would close that
	// gap; tracked as a follow-up. See CRE-4409.
	// The job-spec launch path has no registry OCR3 config to thread; NewServices falls
	// back to the cached OCRConfigService when available.
	return d.NewServices(ctx, command, configJSON, spec.ID, spec.Name.ValueOrZero(), spec.ExternalJobID, &spec.StandardCapabilitiesSpec.OracleFactory, 0, nil)
```

**File:** core/services/standardcapabilities/delegate.go (L503-529)
```go
func ValidatedStandardCapabilitiesSpec(tomlString string) (job.Job, error) {
	jb := job.Job{ExternalJobID: uuid.New()}

	tree, err := toml.Load(tomlString)
	if err != nil {
		return jb, errors.Wrap(err, "toml error on load standard capabilities")
	}

	err = tree.Unmarshal(&jb)
	if err != nil {
		return jb, errors.Wrap(err, "toml unmarshal error on standard capabilities spec")
	}

	var spec job.StandardCapabilitiesSpec
	err = tree.Unmarshal(&spec)
	if err != nil {
		return jb, errors.Wrap(err, "toml unmarshal error on standard capabilities job")
	}

	jb.StandardCapabilitiesSpec = &spec
	if jb.Type != job.StandardCapabilities {
		return jb, errors.Errorf("standard capabilities unsupported job type %s", jb.Type)
	}

	if len(jb.StandardCapabilitiesSpec.Command) == 0 {
		return jb, errors.Errorf("standard capabilities command must be set")
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

**File:** core/web/jobs_controller.go (L217-259)
```go
func (jc *JobsController) validateJobSpec(ctx context.Context, tomlString string) (jb job.Job, statusCode int, err error) {
	jobType, err := job.ValidateSpec(tomlString)
	if err != nil {
		return jb, http.StatusUnprocessableEntity, errors.Wrap(err, "failed to parse TOML")
	}
	config := jc.App.GetConfig()
	switch jobType {
	case job.OffchainReporting:
		jb, err = ocr.ValidatedOracleSpecToml(config, jc.App.GetRelayers().LegacyEVMChains(), tomlString) //nolint:staticcheck // LegacyEVMChains is deprecated but refactoring to new relayer interface requires larger architectural changes
		if !config.OCR().Enabled() {
			return jb, http.StatusNotImplemented, errors.New("The Offchain Reporting feature is disabled by configuration")
		}
	case job.OffchainReporting2:
		jb, err = validate.ValidatedOracleSpecToml(ctx, config.OCR2(), config.Insecure(), tomlString, jc.App.GetLoopRegistrarConfig())
		if !config.OCR2().Enabled() {
			return jb, http.StatusNotImplemented, errors.New("The Offchain Reporting 2 feature is disabled by configuration")
		}
	case job.DirectRequest:
		return jb, http.StatusUnprocessableEntity, errors.New("job type directrequest has been removed and is no longer supported")
	case job.FluxMonitor:
		return jb, http.StatusUnprocessableEntity, errors.New("job type fluxmonitor has been removed and is no longer supported")
	case job.Webhook:
		return jb, http.StatusUnprocessableEntity, errors.New("job type webhook has been removed and is no longer supported")
	case job.CRESettings:
		jb, err = cresettings.ValidatedCRESettingsSpec(tomlString)
	case job.Cron:
		jb, err = cron.ValidatedCronSpec(tomlString)
	case job.VRF:
		jb, err = vrfcommon.ValidatedVRFSpec(tomlString)
	case job.BlockhashStore:
		jb, err = blockhashstore.ValidatedSpec(tomlString)
	case job.BlockHeaderFeeder:
		jb, err = blockheaderfeeder.ValidatedSpec(tomlString)
	case job.Bootstrap:
		jb, err = ocrbootstrap.ValidatedBootstrapSpecToml(tomlString)
	case job.Gateway:
		jb, err = gateway.ValidatedGatewaySpec(tomlString)
	case job.Stream:
		jb, err = streams.ValidatedStreamSpec(tomlString)
	case job.Workflow:
		return jb, http.StatusUnprocessableEntity, errors.New("job type workflow has been removed and is no longer supported")
	case job.StandardCapabilities:
		jb, err = standardcapabilities.ValidatedStandardCapabilitiesSpec(tomlString)
```

**File:** core/services/standardcapabilities/standard_capabilities.go (L122-136)
```go
func (s *StandardCapabilities) Start(ctx context.Context) error {
	return s.StartOnce("StandardCapabilities", func() error {
		envVars, err := plugins.ParseEnvFile(env.CapabilitiesPlugin.Env.Get())
		if err != nil {
			return fmt.Errorf("failed to parse capabilities env file: %w", err)
		}
		cmdFn, opts, err := s.pluginRegistrar.RegisterLOOP(plugins.CmdConfig{
			ID:  s.log.Name(),
			Cmd: s.command,
			Env: envVars,
		})
		if err != nil {
			return fmt.Errorf("error registering loop: %w", err)
		}

```

**File:** plugins/cmd.go (L15-27)
```go
// NewCmdFactory is helper to ensure synchronization between the loop registry and os cmd to exec the LOOP
func NewCmdFactory(register func(id string) (*RegisteredLoop, error), lcfg CmdConfig) (func() *exec.Cmd, error) {
	registeredLoop, err := register(lcfg.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to register %s LOOP plugin: %w", lcfg.ID, err)
	}
	return func() *exec.Cmd {
		cmd := exec.Command(lcfg.Cmd) //#nosec G204 -- we control the value of the cmd so the lint/sec error is a false positive
		cmd.Env = append(cmd.Env, lcfg.Env...)
		cmd.Env = append(cmd.Env, registeredLoop.EnvCfg.AsCmdEnv()...)
		return cmd
	}, nil
}
```

**File:** core/services/standardcapabilities/delegate_test.go (L213-225)
```go
	t.Run("unknown command bypasses allowlist check", func(t *testing.T) {
		d := &Delegate{
			localCfg: &stubLocalCapabilities{allowlisted: map[string]bool{"consensus@1.0.0-alpha": true}},
		}
		spec := job.Job{
			ExternalJobID:            uuid.New(),
			StandardCapabilitiesSpec: &job.StandardCapabilitiesSpec{Command: "unknown-binary"},
		}
		// Unknown commands have no capability ID mapping, so the allowlist check is skipped.
		assert.Panics(t, func() {
			_, _ = d.ServicesForSpec(context.Background(), spec)
		})
	})
```

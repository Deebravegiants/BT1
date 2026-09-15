Audit Report

## Title
Authenticated Job-Edit User Can Execute Arbitrary OS Binaries via `StandardCapabilitiesSpec.Command` - (File: core/services/standardcapabilities/delegate.go)

## Summary
Any authenticated user holding the node's "Edit" role (not Admin) can submit a `standardcapabilities` job spec whose `command` field is an attacker-controlled filesystem path/binary name, which the node subsequently executes verbatim via `exec.Command` under the node process's OS identity. Job creation via both the REST endpoint `POST /v2/jobs` and the GraphQL `createJob` mutation is gated only by `RequiresEditRole`/`authenticateUserCanEdit`, confirmed at [1](#0-0) and [2](#0-1) , so this is a genuine privilege escalation from Edit-role to arbitrary OS command execution on the node host.

## Finding Description
`ValidatedStandardCapabilitiesSpec` only checks that `Command` is non-empty before accepting the job spec: [3](#0-2) . When the job spawner starts the job, `Delegate.ServicesForSpec` extracts `command := spec.StandardCapabilitiesSpec.Command` directly from the untrusted spec: [4](#0-3) . Unless the resolved capability ID happens to match an admin-configured `RegistryBasedLaunchAllowlist` regex — which is empty by default and, per the delegate's own tests, is bypassed entirely for unknown/unmapped commands — the value flows straight to `NewStandardCapabilities(...)`, which registers it as a LOOP subprocess on `Start()`: [5](#0-4) . The actual OS execution occurs in `plugins.NewCmdFactory`, which calls `exec.Command(lcfg.Cmd)` on the caller-supplied string, with a source comment incorrectly assuming the caller controls/validates the value: [6](#0-5) . The delegate's own test explicitly documents that unknown commands bypass the allowlist: [7](#0-6) .

Both entry points for job creation (`POST /v2/jobs` via `auth.RequiresEditRole(jc.Create)` and GraphQL `createJob` via `authenticateUserCanEdit`) require only the Edit role, not Admin: [1](#0-0) [8](#0-7) . This confirms the claim's core premise: the API surface reachable by an Edit-role (non-Admin) user leads directly to unvalidated OS command execution, and no existing authorization or validation layer blocks it in the default configuration.

## Impact Explanation
An authenticated user with only Edit privileges can achieve arbitrary OS command execution on the Chainlink node host, running as the node process's OS identity. This is a severe, in-scope impact: it enables exfiltration of node private keys and database credentials, tampering with on-chain oracle reports, and full node compromise — constituting privilege escalation from a job-edit role to server-process-level code execution.

## Likelihood Explanation
Exploitation requires only the ability to authenticate with Edit role and submit a standard job creation request (`POST /v2/jobs` or `createJob` GraphQL mutation) — no Admin role, database access, or host access is needed. The default configuration of `RegistryBasedLaunchAllowlist` (empty) does not block this; the delegate's own tests confirm unmapped/unknown commands bypass the check entirely. This makes exploitation deterministic and repeatable in any node using default settings.

## Recommendation
- Restrict creation/update of `standardcapabilities` job specs to Admin-only role, given that the `command` field grants OS-level execution capability distinct from other job types.
- Validate the `command` value against a fixed, operator-approved set of binaries/paths at spec-validation time in `ValidatedStandardCapabilitiesSpec`, independent of the opt-in `RegistryBasedLaunchAllowlist`.
- Resolve `command` only from a fixed installation directory (basename-only, no arbitrary path) rather than passing a free-form job-spec string directly to `exec.Command`.
- Add distinct audit logging/alerting for `standardcapabilities` job creation given its OS-execution capability.

## Proof of Concept
1. Authenticate as a user with Edit role (not Admin) against the node's API.
2. Submit via `POST /v2/jobs` (or GraphQL `createJob`):
```
type = "standardcapabilities"
schemaVersion = 1
name = "poc"
command = "/tmp/attacker_payload"
config = ""
```
3. `ValidatedStandardCapabilitiesSpec` accepts it since it only checks `Command != ""` [9](#0-8) .
4. On job start, `Delegate.ServicesForSpec` → `NewStandardCapabilities.Start()` → `plugins.NewCmdFactory` executes `exec.Command("/tmp/attacker_payload")` as the node process [4](#0-3) [10](#0-9) .
5. A Go unit test extending `delegate_test.go`'s existing "unknown command bypasses allowlist check" pattern, combined with an integration test asserting `jc.Create` succeeds for an Edit-role session with this TOML, would concretely demonstrate the end-to-end reachability from the authenticated API down to `exec.Command`.

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

**File:** core/web/resolver/mutation.go (L1061-1113)
```go
func (r *Resolver) CreateJob(ctx context.Context, args struct {
	Input struct {
		TOML string
	}
}) (*CreateJobPayloadResolver, error) {
	if err := authenticateUserCanEdit(ctx); err != nil {
		return nil, err
	}

	jbt, err := job.ValidateSpec(args.Input.TOML)
	if err != nil {
		return NewCreateJobPayload(r.App, nil, map[string]string{
			"TOML spec": errors.Wrap(err, "failed to parse TOML").Error(),
		}), nil
	}

	var jb job.Job
	config := r.App.GetConfig()
	switch jbt {
	case job.OffchainReporting:
		jb, err = ocr.ValidatedOracleSpecToml(config, r.App.GetRelayers().LegacyEVMChains(), args.Input.TOML) //nolint:staticcheck // LegacyEVMChains is deprecated but refactoring to new relayer interface requires larger architectural changes
		if !config.OCR().Enabled() {
			return nil, errors.New("The Offchain Reporting feature is disabled by configuration")
		}
	case job.OffchainReporting2:
		jb, err = validate.ValidatedOracleSpecToml(ctx, r.App.GetConfig().OCR2(), r.App.GetConfig().Insecure(), args.Input.TOML, r.App.GetLoopRegistrarConfig())
		if !config.OCR2().Enabled() {
			return nil, errors.New("The Offchain Reporting 2 feature is disabled by configuration")
		}
	case job.DirectRequest:
		return nil, fmt.Errorf("cannot create job of type %q: %w", job.DirectRequest, job.ErrJobTypeRemoved)
	case job.FluxMonitor:
		return nil, fmt.Errorf("cannot create job of type %q: %w", job.FluxMonitor, job.ErrJobTypeRemoved)
	case job.Webhook:
		return nil, fmt.Errorf("cannot create job of type %q: %w", job.Webhook, job.ErrJobTypeRemoved)
	case job.CRESettings:
		jb, err = cresettings.ValidatedCRESettingsSpec(args.Input.TOML)
	case job.Cron:
		jb, err = cron.ValidatedCronSpec(args.Input.TOML)
	case job.VRF:
		jb, err = vrfcommon.ValidatedVRFSpec(args.Input.TOML)
	case job.BlockhashStore:
		jb, err = blockhashstore.ValidatedSpec(args.Input.TOML)
	case job.BlockHeaderFeeder:
		jb, err = blockheaderfeeder.ValidatedSpec(args.Input.TOML)
	case job.Bootstrap:
		jb, err = ocrbootstrap.ValidatedBootstrapSpecToml(args.Input.TOML)
	case job.Gateway:
		jb, err = gateway.ValidatedGatewaySpec(args.Input.TOML)
	case job.Workflow:
		return nil, fmt.Errorf("cannot create job of type %q: %w", job.Workflow, job.ErrJobTypeRemoved)
	case job.StandardCapabilities:
		jb, err = standardcapabilities.ValidatedStandardCapabilitiesSpec(args.Input.TOML)
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

**File:** core/services/standardcapabilities/standard_capabilities.go (L122-140)
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

		s.capabilitiesLoop = loop.NewStandardCapabilitiesService(s.log, opts, cmdFn)
		if err = s.capabilitiesLoop.Start(ctx); err != nil {
			return fmt.Errorf("error starting standard capabilities service: %w", err)
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

### Title
Authenticated Job-Edit User Can Execute Arbitrary OS Binaries via `StandardCapabilitiesSpec.Command` - (File: core/services/standardcapabilities/delegate.go)

### Summary
Any authenticated user holding the node's "Edit" (or higher) role can submit a `standardcapabilities` job spec whose `command` field is an attacker-supplied, unvalidated filesystem path/binary name. The node subsequently executes that value verbatim via `os/exec.Command` under the server process's OS identity, functionally equivalent to the Langflow analog where a low-privileged "flow user" plants a crafted field that a later "build" step executes as an OS command.

### Finding Description
When a job of type `standardcapabilities` is created (via REST `POST /v2/jobs` or GraphQL `CreateJob`), the TOML is parsed by `ValidatedStandardCapabilitiesSpec`, which only checks that `Command` is non-empty: [1](#0-0) 

The job is persisted (`orm.CreateJob`) and then started by the job spawner, which calls the standard-capabilities `Delegate.ServicesForSpec`, extracting `command := spec.StandardCapabilitiesSpec.Command` directly from the untrusted job spec: [2](#0-1) 

Unless the resolved capability ID happens to match an admin-configured `RegistryBasedLaunchAllowlist` regex, the command passes straight through to `NewStandardCapabilities(...)`, which on `Start()` registers and executes it as a LOOP subprocess: [3](#0-2) 

The actual OS execution happens in `plugins.NewCmdFactory`, which calls `exec.Command(lcfg.Cmd)` with the caller-controlled string, explicitly acknowledged in the source comment as relying on the caller to have validated the value ("we control the value of the cmd" — which is not true for this path): [4](#0-3) 

The only mitigation, `RegistryBasedLaunchAllowlist`, is an opt-in, pattern-based allowlist that must be explicitly configured by an operator; by default it is empty, so it blocks nothing, and its own tests confirm unknown/unmapped commands "bypass the allowlist check" entirely: [5](#0-4) 

This mirrors the Langflow CVE-2026-19295 pattern: an authenticated, non-admin actor supplies a crafted "type"/command value in a spec object, and a subsequent build/start step executes it as an OS-level command under the server's process identity — bypassing what should be an administrative control (`RegistryBasedLaunchAllowlist`, analogous to `LANGFLOW_ALLOW_CUSTOM_COMPONENTS=false`).

### Impact Explanation
Any user with Edit privileges (not necessarily Admin) can achieve arbitrary OS command execution on the Chainlink node host, running as the node's OS process identity. This can lead to full compromise of the node — including exfiltration of private keys, database credentials, and other secrets held by the node process, tampering with on-chain transactions/oracle reports, and lateral movement within the deployment. This is privilege escalation from "job-edit user" to arbitrary code execution at the server-process level.

### Likelihood Explanation
Exploitation requires only the ability to create a job via the standard REST (`/v2/jobs`) or GraphQL (`CreateJob`) mutation, gated by role checks (`authenticateUserCanEdit` / `RequiresEditorRole`) rather than by Admin-only restriction. No malicious peer, network-layer, or operator-mode assumption is required — a single authenticated Edit-role API call/UI action is sufficient. The default configuration (`RegistryBasedLaunchAllowlist = []`) does not block this at all, so likelihood is high in any node that has not manually hardened this list.

### Recommendation
- Restrict creation/update of `standardcapabilities` (and any other job type whose spec embeds an executable `command`) to Admin-only role, not Edit.
- Validate/allowlist the `command` value against a fixed, operator-approved set of binaries at spec-validation time (`ValidatedStandardCapabilitiesSpec`), rather than relying solely on the opt-in `RegistryBasedLaunchAllowlist` regex list.
- Consider resolving `command` only from a fixed installation directory (basename-only, no path traversal) rather than passing a free-form job-spec string straight to `exec.Command`.
- Audit-log and alert on `standardcapabilities` job creation events distinctly, given their OS-execution capability.

### Proof of Concept
1. Authenticate as a user with Edit role (not necessarily Admin) against the node's API.
2. Submit a job via `POST /v2/jobs` (or the `createJob` GraphQL mutation) with TOML:
```
type = "standardcapabilities"
schemaVersion = 1
name = "poc"
command = "/tmp/attacker_payload"
config = ""
```
3. The node accepts and creates the job (`ValidatedStandardCapabilitiesSpec` only checks `Command != ""`).
4. On job start, `Delegate.ServicesForSpec` → `NewStandardCapabilities` → `plugins.NewCmdFactory` executes `exec.Command("/tmp/attacker_payload")` as the node process, running the attacker's binary with the node's OS privileges. [2](#0-1) [4](#0-3)

### Citations

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

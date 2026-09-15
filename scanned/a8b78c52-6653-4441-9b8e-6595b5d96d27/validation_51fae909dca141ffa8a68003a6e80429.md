Confirmed: `plugins.NewCmdFactory` at [1](#0-0)  directly calls `exec.Command(lcfg.Cmd)` with the operator/job-spec-supplied `Cmd` string — the `#nosec G204` comment explicitly notes this bypasses static analysis under the assumption that "we control the value of the cmd," but the value originates from a job spec field that a non-admin, edit-role authenticated user can set via the standard HTTP/GraphQL job-creation APIs.

### Title
Authenticated edit-role user can execute arbitrary binaries on the Chainlink node via `standardcapabilities` job spec `command` field — (File: `core/services/standardcapabilities/delegate.go`)

### Summary
The `standardcapabilities` job type accepts a free-form `command` string that is later passed unmodified to `exec.Command()` and executed as a subprocess on the node host. Job creation via `POST /v2/jobs` and the `createJob` GraphQL mutation only requires `RequiresEditRole`/`authenticateUserCanEdit`, not admin. This lets any authenticated "edit" user cause the node process to `fork/exec` an arbitrary path they control, mirroring the Gerapy CVE-2021-32849 pattern where an authenticated (non-privileged) user could trigger arbitrary command execution through a normally-scoped API.

### Finding Description
`ValidatedStandardCapabilitiesSpec` only checks that `Command` is non-empty; it performs no allowlisting or path restriction beyond the `IsAllowlisted` local-config check on capability ID, which is itself bypassable for any command whose derived capability ID is empty or not in the allowlist map (see `Test_ServicesForSpec_AllowlistEnforcement`/"unknown command bypasses allowlist check" at [2](#0-1) ): [3](#0-2) 

The command flows to `Delegate.NewServices` → `s.pluginRegistrar.RegisterLOOP` → `plugins.NewCmdFactory`, which builds and returns `exec.Command(lcfg.Cmd)`: [4](#0-3) [5](#0-4) 

The job-creation entry points that let a user set this `command` value require only an edit-role session/API token, not admin: [6](#0-5) [7](#0-6) [8](#0-7) 

Unlike the OCR2 generic-plugin path, which calls `exec.LookPath(command)` as a soft sanity check ( [9](#0-8) ), the `standardcapabilities` path does no such check at validation time — `NewCmdFactory` will happily attempt to exec whatever string is provided (absolute path, relative path, or PATH-resolved binary name), as demonstrated by the test helper `createValidJobSpec` at [10](#0-9)  which sets `command = "/home/capabilities/nowhere"`.

### Impact Explanation
An edit-role user (a role explicitly below admin in the RBAC model defined in [11](#0-10) ) can cause the node to execute any binary/script reachable on the node's filesystem or `$PATH`, with the node process's environment and privileges. If the attacker can also place or influence a file at a predictable path (e.g., via another writable feature, a shared volume, or a path they control such as a script under a world-writable temp dir), this becomes full arbitrary command execution equivalent to the Gerapy CVE. Even without planting a new binary, an edit user can pivot existing trusted binaries on the host into unintended execution contexts and can enumerate/probe the filesystem via error messages (`exec.LookPath`/`cmd.Run` failures leak path existence).

### Likelihood Explanation
High for edit-role token holders: job creation via `POST /v2/jobs` or GraphQL `createJob` is a standard, well-documented operator workflow, and `standardcapabilities` is a supported, non-experimental job type. No additional privilege escalation is needed beyond obtaining an edit-role API token, which is a normal operational credential in multi-user Chainlink node deployments.

### Recommendation
Restrict `command` in `standardcapabilities` job specs to a server-side allowlist of known capability binaries (extending the existing `IsAllowlisted`/`RegistryBasedLaunchAllowlist` mechanism to be default-deny rather than opt-in), and/or require admin role for creating/updating `standardcapabilities` jobs given their direct subprocess-execution semantics. At minimum, validate `command` against a configured directory of approved binaries and reject arbitrary paths, matching or exceeding the `exec.LookPath` check already used for OCR2 generic plugins.

### Proof of Concept
1. Obtain an edit-role session or API token (`POST /v2/jobs` is gated by `auth.RequiresEditRole`, not `RequiresAdminRole` — see [6](#0-5) ).
2. Submit a job spec:
```
type = "standardcapabilities"
schemaVersion = 1
name = "poc"
externalJobID = "<uuid>"
forwardingAllowed = false
command = "/tmp/attacker_controlled_script"
config = ""
```
via `POST /v2/jobs` with `{"toml": "<spec above>"}`.
3. `ValidatedStandardCapabilitiesSpec` accepts it (only checks `Command != ""`), `AddJobV2` persists and starts it, and `Delegate.ServicesForSpec` → `NewServices` → `StandardCapabilities.Start` invokes `RegisterLOOP`/`NewCmdFactory`, causing the node process to `exec.Command("/tmp/attacker_controlled_script")`.

### Citations

**File:** plugins/cmd.go (L15-26)
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

**File:** core/web/router.go (L391-396)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
```

**File:** core/web/resolver/mutation.go (L1061-1075)
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
```

**File:** core/web/resolver/mutation.go (L1112-1113)
```go
	case job.StandardCapabilities:
		jb, err = standardcapabilities.ValidatedStandardCapabilitiesSpec(args.Input.TOML)
```

**File:** core/services/ocr2/validate/validate.go (L248-262)
```go
	plugEnv := env.NewPlugin(p.PluginName)

	command := p.Command
	if command == "" {
		command = plugEnv.Cmd.Get()
	}

	if command == "" {
		return errors.New("generic config invalid: no command found")
	}

	_, err = exec.LookPath(command)
	if err != nil {
		return fmt.Errorf("failed to find binary  %q", command)
	}
```

**File:** deployment/environment/test/job_service_client_test.go (L1050-1062)
```go
// need some non-ocr job type to avoid the ocr validation and the p2pwrapper check
func createValidJobSpec(externalJobID string) string {
	tomlString := `
type = "standardcapabilities"
schemaVersion = 1
externalJobID = "%s"
name = "hacking-%s"
forwardingAllowed = false
command = "/home/capabilities/nowhere"
config = ""
`
	return fmt.Sprintf(tomlString, externalJobID, externalJobID)
}
```

**File:** core/web/auth/auth.go (L217-234)
```go
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

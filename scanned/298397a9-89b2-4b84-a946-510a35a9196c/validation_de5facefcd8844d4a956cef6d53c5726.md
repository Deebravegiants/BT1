## Analysis

I found a strong analog for the "unprivileged actor forces an unintended state transition on a critical resource" bug class in the External Initiator role/authorization design.

The role hierarchy is `admin` > `edit` > `run` > `view`, defined at [1](#0-0) . Any External Initiator (an unprivileged, remote, network-facing caller authenticated only by a bearer access-key/secret pair meant solely to trigger job runs) is automatically granted the `run` role at authentication time: [2](#0-1) . `RequiresRunRole` only checks that the role is not `view` — it does not distinguish between a real human "run"-level user and an External Initiator: [3](#0-2) .

That `run`-gated permission is applied to node-operational endpoints that go well beyond "triggering job runs" and can disrupt core node functionality:
- `ReplayFromBlock` — forces the node to reprocess/replay chain blocks from an arbitrary block number: [4](#0-3) [5](#0-4) 
- `LPSkipToBlock` — repositions the LogPoller's processing cursor to an arbitrary block: [6](#0-5) [7](#0-6) 
- `FindLCA` and (in dev builds) `ExecuteCapability`: [8](#0-7) 

An External Initiator credential (`X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret`) is provisioned to third-party, less-trusted integrations specifically to POST job-run triggers over the network — this is the closest analog to the raffle contract's "temporary/limited-purpose caller." Because the middleware collapses that limited-purpose identity into the generic `run` role without any endpoint-level distinction between "the caller may create job runs" and "the caller may reconfigure block processing/log polling for the whole node," a compromised or malicious external initiator can call `ReplayFromBlock`/`LPSkipToBlock` repeatedly to force expensive, disruptive reprocessing of chain history, similar in spirit to `cancelRaffle` letting an under-privileged caller repeatedly force the raffle system back into a non-operational state.

However, I could not find any additional privilege check inside `ReplayController.ReplayFromBlock` or `LPSkipController.LPSkipToBlock` beyond the router-level `RequiresRunRole` — I was not able to fully trace `App.ReplayFromBlock` / `App.LPSkipToBlock` downstream implementations (e.g., whether replay/log-poller-skip operations are rate-limited, whether they can be triggered concurrently with unbounded resource cost, or whether the "PoC" impact would be a genuine DoS vs. a bounded, intended admin operation) due to remaining iteration limits. This is a design/least-privilege observation rather than a confirmed exploited state-transition bug like `cancelRaffle`, since External Initiators are a documented, operator-provisioned credential (not an arbitrary unauthenticated caller), and I did not verify how commonly operators actually grant EI credentials versus dedicated `run`-role human accounts.

### Title
External Initiator credentials (intended only to trigger job runs) inherit the `run` role and can call node-disrupting endpoints (`ReplayFromBlock`, `LPSkipToBlock`) - (File: core/web/auth/auth.go, core/web/router.go)

### Summary
`AuthenticateExternalInitiator` unconditionally assigns the `run` role to any authenticated external initiator, and several router endpoints that can disrupt core node chain-processing (`ReplayFromBlock`, `LPSkipToBlock`, `FindLCA`) are gated only by `RequiresRunRole`, which does not distinguish an External Initiator (meant only to POST job-run triggers) from a genuine `run`-role human user.

### Finding Description
`AuthenticateExternalInitiator` sets `c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})` for any request successfully authenticated via EI access-key/secret headers [2](#0-1) . `RequiresRunRole` grants access to any handler as long as `user.Role != clsessions.UserRoleView` [3](#0-2) , so it cannot differentiate "a caller meant only to launch webhook job runs" from "a caller entitled to perform node administration actions." The router applies this same guard to `ReplayFromBlock`, `FindLCA`, and `LPSkipToBlock` [9](#0-8) , which allow reprocessing of chain history / repositioning the LogPoller cursor [5](#0-4) [7](#0-6) .

### Impact Explanation
An External Initiator credential — the lowest-trust, network-facing authentication mechanism specifically scoped to triggering job runs — can be reused to force the node to replay blocks or reposition log processing arbitrarily and repeatedly, potentially causing significant reprocessing overhead / resource exhaustion or interfering with in-flight chain monitoring, similar in effect to the raffle-cancellation griefing pattern (a limited-purpose caller repeatedly forcing the system back into a costly/disrupted operational state).

### Likelihood Explanation
Exploitation requires possession of a valid EI access-key/secret, which an operator issues to third-party or lower-trust integrations. Given that EI credentials are the intended external-facing pathway per the "external-initiator handling" area, and that no endpoint distinguishes EI-originated `run` role from admin-provisioned `run` role, likelihood is moderate — contingent on how broadly operators deploy EI credentials and whether they are treated as fully trusted internally (unverified in this review).

### Recommendation
Introduce a distinct authorization scope for External Initiators separate from the generic `run` role (e.g., restrict EI-authenticated sessions to only the job-run trigger endpoint), or explicitly exclude `ReplayFromBlock`/`LPSkipToBlock`/`FindLCA` from roles obtainable via EI authentication, e.g. by checking `GetAuthenticatedExternalInitiator` and rejecting those routes for EI-originated sessions.

### Proof of Concept
Not independently verified against a running node in this review; conceptually: authenticate with valid EI headers (`X-Chainlink-EA-AccessKey`/`X-Chainlink-EA-Secret`) as done in `TestTokenAuthRequired_BadTokenCredentials` [10](#0-9) , then issue repeated `POST /v2/replay_from_block/:number` or `POST /v2/lp_skip_to_block` requests using those same headers to trigger repeated chain reprocessing.

### Citations

**File:** core/sessions/user.go (L27-34)
```go
type UserRole string

const (
	UserRoleAdmin UserRole = "admin"
	UserRoleEdit  UserRole = "edit"
	UserRoleRun   UserRole = "run"
	UserRoleView  UserRole = "view"
)
```

**File:** core/web/auth/auth.go (L143-149)
```go
	// External initiator endpoints (wrapped with AuthenticateExternalInitiator) inherently assume the role
	// of 'run' (required to trigger job runs)
	c.Set(SessionExternalInitiatorKey, ei)
	c.Set(SessionUserKey, &clsessions.User{Role: clsessions.UserRoleRun})

	return nil
}
```

**File:** core/web/auth/auth.go (L198-215)
```go
// RequiresRunRole extracts the user object from the context, and asserts the user's role is at least
// 'run'
func RequiresRunRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/router.go (L297-306)
```go
		rc := ReplayController{app}
		authv2.POST("/replay_from_block/:number", auth.RequiresRunRole(rc.ReplayFromBlock))
		lcaC := LCAController{app}
		authv2.GET("/find_lca", auth.RequiresRunRole(lcaC.FindLCA))
		lpSkipC := LPSkipController{app}
		authv2.POST("/lp_skip_to_block", auth.RequiresRunRole(lpSkipC.LPSkipToBlock))

		if build.IsDev() {
			capContr := CapabilityController{app}
			authv2.POST("/execute_capability", auth.RequiresRunRole(capContr.ExecuteCapability))
```

**File:** core/web/replay_controller.go (L18-65)
```go
// ReplayFromBlock causes the node to process blocks again from the given block number
// Example:
//
//	"<application>/v2/replay_from_block/:number"
func (bdc *ReplayController) ReplayFromBlock(c *gin.Context) {
	if c.Param("number") == "" {
		jsonAPIError(c, http.StatusUnprocessableEntity, errors.New("missing 'number' parameter"))
		return
	}

	// check if "force" query string parameter provided
	var force bool
	var err error
	if fb := c.Query("force"); fb != "" {
		force, err = strconv.ParseBool(fb)
		if err != nil {
			jsonAPIError(c, http.StatusUnprocessableEntity, errors.Wrap(err, "boolean value required for 'force' query string param"))
			return
		}
	}

	blockNumber, err := strconv.ParseInt(c.Param("number"), 10, 0)
	if err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	if blockNumber < 0 {
		jsonAPIError(c, http.StatusUnprocessableEntity, errors.Errorf("block number cannot be negative: %v", blockNumber))
		return
	}

	chainFamily := c.Query("family")
	if chainFamily == "" {
		jsonAPIError(c, http.StatusUnprocessableEntity, errors.New("chain family was not provided"))
		return
	}

	chainID := c.Query("ChainID")
	if strings.TrimSpace(chainID) == "" {
		jsonAPIError(c, http.StatusUnprocessableEntity, errors.New("chain-id was not provided"))
		return
	}

	ctx := c.Request.Context()
	if err := bdc.App.ReplayFromBlock(ctx, chainFamily, chainID, uint64(blockNumber), force); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}
```

**File:** core/web/lp_skip_controller.go (L24-61)
```go
// LPSkipToBlock repositions the LogPoller to start processing from the given block number.
// Example:
//
//	"<application>/v2/lp_skip_to_block"
func (c *LPSkipController) LPSkipToBlock(gctx *gin.Context) {
	var request LPSkipToBlockRequest
	if err := gctx.ShouldBindJSON(&request); err != nil {
		jsonAPIError(gctx, http.StatusUnprocessableEntity, err)
		return
	}
	if request.BlockNumber < 2 {
		jsonAPIError(gctx, http.StatusUnprocessableEntity, errors.Errorf("block number must be >= 2: %v", request.BlockNumber))
		return
	}

	if request.Family == "" {
		jsonAPIError(gctx, http.StatusUnprocessableEntity, errors.New("chain family was not provided"))
		return
	}
	if request.Family != relay.NetworkEVM {
		jsonAPIError(gctx, http.StatusUnprocessableEntity, errors.Errorf("unsupported chain family %q, only %s is supported", request.Family, relay.NetworkEVM))
		return
	}

	if strings.TrimSpace(request.ChainID) == "" {
		jsonAPIError(gctx, http.StatusUnprocessableEntity, errors.New("chain-id was not provided"))
		return
	}

	ctx := gctx.Request.Context()
	if err := c.App.LPSkipToBlock(ctx, request.Family, request.ChainID, request.BlockNumber); err != nil {
		if errors.Is(err, chainlink.ErrNoSuchRelayer) {
			jsonAPIError(gctx, http.StatusBadRequest, err)
			return
		}
		jsonAPIError(gctx, http.StatusInternalServerError, err)
		return
	}
```

**File:** core/web/router_test.go (L103-118)
```go
	eia := auth.NewToken()
	url := cltest.WebURL(t, "http://localhost:8888")
	eir := &bridges.ExternalInitiatorRequest{
		Name: uuid.New().String(),
		URL:  &url,
	}
	ea, err := bridges.NewExternalInitiator(eia, eir)
	require.NoError(t, err)
	err = app.BridgeORM().CreateExternalInitiator(ctx, ea)
	require.NoError(t, err)

	request, err := http.NewRequestWithContext(ctx, http.MethodGet, ts.URL+"/v2/ping/", bytes.NewBufferString("{}"))
	require.NoError(t, err)
	request.Header.Set("Content-Type", web.MediaType)
	request.Header.Set("X-Chainlink-EA-AccessKey", eia.AccessKey)
	request.Header.Set("X-Chainlink-EA-Secret", "every unpleasant commercial color from aquamarine to beige")
```

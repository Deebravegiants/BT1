No vulnerability found for this question.

Based on the investigation, Chainlink's node API implements RBAC via `auth.RequiresAdminRole`, `auth.RequiresEditRole`, and `auth.RequiresRunRole` middleware in `core/web/auth/auth.go` [1](#0-0) , and these are consistently applied to mutating routes (users, bridges, keys, transfers, jobs, external initiators) in `core/web/router.go` [2](#0-1) . The `ConfigController.Show` endpoint, the closest analog to the Gerrit plugin's config-management surface, is read-only (`GET /v2/config`, `GET /v2/config/v2`) with no corresponding POST/PATCH to mutate global config exposed to lower-privileged roles [3](#0-2) . The three endpoints without explicit role middleware (`PATCH /v2/user/password`, `POST /v2/user/token`, `POST /v2/user/token/delete`) only ever operate on the calling session's own user record and require re-verification of the current password before mutating state [4](#0-3) [5](#0-4) , so they don't allow a view-only user to affect another user's account or global configuration. There is a dedicated RBAC test suite (`TestRBAC_Routemap_*`) that asserts every route's role requirement against a `routesRolesMap` table [6](#0-5) , which does not reveal a route where a view/read-only actor can mutate configuration analogous to GHSA-4vf2-cm23-rf4c.

### Citations

**File:** core/web/auth/auth.go (L198-253)
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

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/router.go (L238-335)
```go
func v2Routes(app chainlink.Application, r *gin.RouterGroup) {
	unauthedv2 := r.Group("/v2")

	prc := PipelineRunsController{app}
	psec := PipelineJobSpecErrorsController{app}
	unauthedv2.PATCH("/resume/:runID", prc.Resume)

	authv2 := r.Group("/v2", auth.Authenticate(app.AuthenticationProvider(),
		auth.AuthenticateByToken,
		auth.AuthenticateBySession,
	))
	{
		uc := UserController{app}
		authv2.GET("/users", auth.RequiresAdminRole(uc.Index))
		authv2.POST("/users", auth.RequiresAdminRole(uc.Create))
		authv2.PATCH("/users", auth.RequiresAdminRole(uc.UpdateRole))
		authv2.DELETE("/users/:email", auth.RequiresAdminRole(uc.Delete))
		authv2.PATCH("/user/password", uc.UpdatePassword)
		authv2.POST("/user/token", uc.NewAPIToken)
		authv2.POST("/user/token/delete", uc.DeleteAPIToken)

		wa := NewWebAuthnController(app)
		authv2.GET("/enroll_webauthn", wa.BeginRegistration)
		authv2.POST("/enroll_webauthn", wa.FinishRegistration)

		eia := ExternalInitiatorsController{app}
		authv2.GET("/external_initiators", paginatedRequest(eia.Index))
		authv2.POST("/external_initiators", auth.RequiresEditRole(eia.Create))
		authv2.DELETE("/external_initiators/:Name", auth.RequiresEditRole(eia.Destroy))

		bt := BridgeTypesController{app}
		authv2.GET("/bridge_types", paginatedRequest(bt.Index))
		authv2.POST("/bridge_types", auth.RequiresEditRole(bt.Create))
		authv2.GET("/bridge_types/:BridgeName", bt.Show)
		authv2.PATCH("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Update))
		authv2.DELETE("/bridge_types/:BridgeName", auth.RequiresEditRole(bt.Destroy))

		ets := EVMTransfersController{app}
		authv2.POST("/transfers", auth.RequiresAdminRole(ets.Create))
		authv2.POST("/transfers/evm", auth.RequiresAdminRole(ets.Create))
		tts := CosmosTransfersController{app}
		authv2.POST("/transfers/cosmos", auth.RequiresAdminRole(tts.Create))
		sts := SolanaTransfersController{app}
		authv2.POST("/transfers/solana", auth.RequiresAdminRole(sts.Create))

		cc := ConfigController{app}
		authv2.GET("/config", cc.Show)
		authv2.GET("/config/v2", cc.Show)

		tas := TxAttemptsController{app}
		authv2.GET("/tx_attempts", paginatedRequest(tas.Index))
		authv2.GET("/tx_attempts/evm", paginatedRequest(tas.Index))

		txs := TransactionsController{app}
		authv2.GET("/transactions/evm", paginatedRequest(txs.Index))
		authv2.GET("/transactions/evm/:TxHash", txs.Show)
		authv2.GET("/transactions", paginatedRequest(txs.Index))
		authv2.GET("/transactions/:TxHash", txs.Show)

		rc := ReplayController{app}
		authv2.POST("/replay_from_block/:number", auth.RequiresRunRole(rc.ReplayFromBlock))
		lcaC := LCAController{app}
		authv2.GET("/find_lca", auth.RequiresRunRole(lcaC.FindLCA))
		lpSkipC := LPSkipController{app}
		authv2.POST("/lp_skip_to_block", auth.RequiresRunRole(lpSkipC.LPSkipToBlock))

		if build.IsDev() {
			capContr := CapabilityController{app}
			authv2.POST("/execute_capability", auth.RequiresRunRole(capContr.ExecuteCapability))
		}

		csakc := CSAKeysController{app}
		authv2.GET("/keys/csa", csakc.Index)
		authv2.POST("/keys/csa", auth.RequiresEditRole(csakc.Create))
		authv2.POST("/keys/csa/import", auth.RequiresAdminRole(csakc.Import))
		authv2.POST("/keys/csa/export/:ID", auth.RequiresAdminRole(csakc.Export))

		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
		// duplicated from above, with `evm` instead of `eth`
		// legacy ones remain for backwards compatibility

		ethKeysGroup := authv2.Group("", auth.Authenticate(app.AuthenticationProvider(),
			auth.AuthenticateByToken,
			auth.AuthenticateBySession,
		))

		ethKeysGroup.Use(ekc.formatETHKeyResponse())
		authv2.GET("/keys/evm", ekc.Index)
		ethKeysGroup.POST("/keys/evm", auth.RequiresEditRole(ekc.Create))
		ethKeysGroup.DELETE("/keys/evm/:address", auth.RequiresAdminRole(ekc.Delete))
		ethKeysGroup.POST("/keys/evm/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/evm/export/:address", auth.RequiresAdminRole(ekc.Export))
		ethKeysGroup.POST("/keys/evm/chain", auth.RequiresAdminRole(ekc.Chain))
```

**File:** core/web/config_controller.go (L19-42)
```go
// Show returns the whitelist of config variables
// Example:
//
//	"<application>/config"
func (cc *ConfigController) Show(c *gin.Context) {
	cfg := cc.App.GetConfig()
	var userOnly bool
	if s, has := c.GetQuery("userOnly"); has {
		var err error
		userOnly, err = strconv.ParseBool(s)
		if err != nil {
			jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("invalid bool for userOnly: %w", err))
			return
		}
	}
	var toml string
	user, effective := cfg.ConfigTOML()
	if userOnly {
		toml = user
	} else {
		toml = effective
	}
	jsonAPIResponse(c, ConfigV2Resource{toml}, "config")
}
```

**File:** core/web/user_controller.go (L202-240)
```go
func (u *UserController) UpdatePassword(c *gin.Context) {
	ctx := c.Request.Context()
	var request UpdatePasswordRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to update password"))
		return
	}
	if !utils.CheckPasswordHash(request.OldPassword, string(user.HashedPassword)) {
		u.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusConflict, errors.New("old password does not match"))
		return
	}
	if err := utils.VerifyPasswordComplexity(request.NewPassword, user.Email); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}
	if err := u.updateUserPassword(c, &user, request.NewPassword); err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	u.App.GetAuditLogger().Audit(audit.PasswordResetSuccess, map[string]any{"user": user.Email})
	jsonAPIResponse(c, presenters.NewUserResource(user), "user")
```

**File:** core/web/user_controller.go (L244-286)
```go
func (u *UserController) NewAPIToken(c *gin.Context) {
	ctx := c.Request.Context()
	var request clsession.ChangeAuthTokenRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		jsonAPIError(c, http.StatusUnprocessableEntity, err)
		return
	}

	sessionUser, ok := webauth.GetAuthenticatedUser(c)
	if !ok {
		jsonAPIError(c, http.StatusInternalServerError, errors.New("failed to obtain current user from context"))
		return
	}
	user, err := u.App.AuthenticationProvider().FindUser(ctx, sessionUser.Email)
	if err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		u.App.GetLogger().Errorf("failed to obtain current user record: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("unable to create API token"))
		return
	}
	// In order to create an API token, login validation with provided password must succeed
	err = u.App.AuthenticationProvider().TestPassword(ctx, sessionUser.Email, request.Password)
	if err != nil {
		u.App.GetAuditLogger().Audit(audit.APITokenCreateAttemptPasswordMismatch, map[string]any{"user": user.Email})
		jsonAPIError(c, http.StatusUnauthorized, errors.New("incorrect password"))
		return
	}
	newToken := auth.NewToken()
	if err := u.App.AuthenticationProvider().SetAuthToken(ctx, &user, newToken); err != nil {
		if errors.Is(err, clsession.ErrNotSupported) {
			jsonAPIError(c, http.StatusBadRequest, errUnsupportedForAuth)
			return
		}
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	u.App.GetAuditLogger().Audit(audit.APITokenCreated, map[string]any{"user": user.Email})
	jsonAPIResponseWithStatus(c, newToken, "auth_token", http.StatusCreated)
}
```

**File:** core/web/auth/auth_test.go (L213-221)
```go
// The following are admin only routes
var routesRolesMap = [...]routeRules{
	{"GET", "/v2/users", false, false, false},
	{"POST", "/v2/users", false, false, false},
	{"PATCH", "/v2/users", false, false, false},
	{"DELETE", "/v2/users/MOCK", false, false, false},
	{"PATCH", "/v2/user/password", true, true, true},
	{"POST", "/v2/user/token", true, true, true},
	{"POST", "/v2/user/token/delete", true, true, true},
```

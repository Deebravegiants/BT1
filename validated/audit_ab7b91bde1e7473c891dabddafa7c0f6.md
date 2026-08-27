No vulnerability found for this question.

**Analysis basis:** The `Authenticator.allowedPaths` map in `anonymous.go` is populated exactly once inside `NewAuthenticator` and never written to again — there is no setter, no exported mutator, and no reference to `allowedPaths` outside that one function and the read in `AuthenticateRequest`. [1](#0-0) 

The only dynamic-reload mechanism in the authentication stack, `updateAuthenticationConfig` / `authenticationConfigUpdater`, only swaps the JWT/OIDC authenticator via an `atomic.Pointer[jwtAuthenticatorWithCancel]`; it never touches or reconstructs the anonymous authenticator or its `allowedPaths` map. [2](#0-1) 

Both call sites that build the anonymous authenticator (`kubeapiserverauthenticator.Config.New` and `authenticatorfactory.DelegatingAuthenticatorConfig.New`) call `anonymous.NewAuthenticator(...)` once at server/authenticator construction time, producing a fresh, immutable map each time a new authenticator chain is built — reconfiguration replaces the whole `*Authenticator` instance rather than mutating an existing one's map in place. [3](#0-2) [4](#0-3) 

Since `allowedPaths` is write-once/read-many and never mutated after construction, there is no mutation entry point for concurrent writers to race against `AuthenticateRequest`'s reads, so the described data race and its resulting anonymous-auth bypass are not reachable in this codebase.

### Citations

**File:** staging/src/k8s.io/apiserver/pkg/authentication/request/anonymous/anonymous.go (L32-62)
```go
type Authenticator struct {
	allowedPaths map[string]bool
}

func (a *Authenticator) AuthenticateRequest(req *http.Request) (*authenticator.Response, bool, error) {
	if len(a.allowedPaths) > 0 && !a.allowedPaths[req.URL.Path] {
		return nil, false, nil
	}

	auds, _ := authenticator.AudiencesFrom(req.Context())
	return &authenticator.Response{
		User: &user.DefaultInfo{
			Name:   anonymousUser,
			Groups: []string{unauthenticatedGroup},
		},
		Audiences: auds,
	}, true, nil
}

// NewAuthenticator returns a new anonymous authenticator.
// When conditions is empty all requests are authenticated as anonymous.
// When conditions are non-empty only those requests that match the at-least one
// condition are authenticated as anonymous.
func NewAuthenticator(conditions []apiserver.AnonymousAuthCondition) authenticator.Request {
	allowedPaths := make(map[string]bool)
	for _, c := range conditions {
		allowedPaths[c.Path] = true
	}

	return &Authenticator{allowedPaths: allowedPaths}
}
```

**File:** pkg/kubeapiserver/authenticator/config.go (L166-193)
```go
	var updateAuthenticationConfig func(context.Context, *apiserver.AuthenticationConfiguration) error
	if config.AuthenticationConfig != nil {
		initialJWTAuthenticator, err := newJWTAuthenticator(serverLifecycle, config.AuthenticationConfig, config.OIDCSigningAlgs, config.APIAudiences, config.ServiceAccountIssuers, config.EgressLookup, config.APIServerID)
		if err != nil {
			return nil, nil, nil, nil, err
		}

		jwtAuthenticatorPtr := &atomic.Pointer[jwtAuthenticatorWithCancel]{}
		jwtAuthenticatorPtr.Store(initialJWTAuthenticator)

		initialIssuers := sets.New[string]()
		for _, jwt := range config.AuthenticationConfig.JWT {
			initialIssuers.Insert(jwt.Issuer.URL)
		}

		updateAuthenticationConfig = (&authenticationConfigUpdater{
			serverLifecycle:     serverLifecycle,
			config:              config,
			jwtAuthenticatorPtr: jwtAuthenticatorPtr,
			issuers:             initialIssuers,
		}).updateAuthenticationConfig

		tokenAuthenticators = append(tokenAuthenticators,
			authenticator.TokenFunc(func(ctx context.Context, token string) (*authenticator.Response, bool, error) {
				return jwtAuthenticatorPtr.Load().jwtAuthenticator.AuthenticateToken(ctx, token)
			}),
		)
	}
```

**File:** pkg/kubeapiserver/authenticator/config.go (L231-246)
```go
	if len(authenticators) == 0 {
		if config.Anonymous.Enabled {
			return anonymous.NewAuthenticator(config.Anonymous.Conditions), nil, &securityDefinitionsV2, securitySchemesV3, nil
		}
		return nil, nil, &securityDefinitionsV2, securitySchemesV3, nil
	}

	authenticator := union.New(authenticators...)

	authenticator = group.NewAuthenticatedGroupAdder(authenticator)

	if config.Anonymous.Enabled {
		// If the authenticator chain returns an error, return an error (don't consider a bad bearer token
		// or invalid username/password combination anonymous).
		authenticator = union.NewFailOnError(authenticator, anonymous.NewAuthenticator(config.Anonymous.Conditions))
	}
```

**File:** staging/src/k8s.io/apiserver/pkg/authentication/authenticatorfactory/delegating.go (L117-128)
```go
	if len(authenticators) == 0 {
		if c.Anonymous != nil && c.Anonymous.Enabled {
			return anonymous.NewAuthenticator(c.Anonymous.Conditions), &securityDefinitions, nil
		}
		return nil, nil, errors.New("no authentication method configured")
	}

	authenticator := group.NewAuthenticatedGroupAdder(unionauth.New(authenticators...))
	if c.Anonymous != nil && c.Anonymous.Enabled {
		authenticator = unionauth.NewFailOnError(authenticator, anonymous.NewAuthenticator(c.Anonymous.Conditions))
	}
	return authenticator, &securityDefinitions, nil
```

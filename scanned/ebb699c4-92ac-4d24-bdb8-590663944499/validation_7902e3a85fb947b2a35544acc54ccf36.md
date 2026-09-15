### Title
SQL Injection via unsanitized `taskName` string interpolation in `FindTaskResultByRunIDAndTaskName` - (File: core/services/job/orm.go)

### Summary
`FindTaskResultByRunIDAndTaskName` builds a SQL statement with `fmt.Sprintf`, splicing the `taskName` argument directly into the query string as a quoted literal rather than passing it as a bound parameter, mirroring the exact bug class in CVE-2017-16893 (Piwigo's `tags.php` splicing the `edit_list` parameter into SQL instead of binding it).

### Finding Description [1](#0-0) 

```go
func (o *orm) FindTaskResultByRunIDAndTaskName(ctx context.Context, runID int64, taskName string) (result []byte, err error) {
	stmt := fmt.Sprintf("SELECT * FROM pipeline_task_runs WHERE pipeline_run_id = $1 AND dot_id = '%s';", taskName)

	var taskRuns []pipeline.TaskRun
	if errB := o.ds.SelectContext(ctx, &taskRuns, stmt, runID); errB != nil {
		return nil, errB
	}
```

The `runID` parameter is correctly bound as `$1`, but `taskName` is interpolated directly into the SQL text via `fmt.Sprintf` and wrapped in single quotes, exactly the pattern flagged in the Piwigo advisory (unsanitized `edit_list` values spliced into a query string). If `taskName` ever contains a single quote or SQL metacharacters, it breaks out of the string literal and can alter the query (e.g., add `OR 1=1`, UNION-based extraction from other tables, etc.), consistent with the classic SQLi construction described in the CVE.

### Impact Explanation
Elsewhere in the same file, the analogous helper `findJob` uses the same unsafe pattern for a column name (`fmt.Sprintf(... jobs.%s = $1 ...)`), but that argument is always a hardcoded literal, so it's not attacker-influenced. `FindTaskResultByRunIDAndTaskName`, however, takes `taskName` as a caller-supplied string with no validation or escaping.

Despite the confirmed unsafe pattern, I could not find any live caller of `FindTaskResultByRunIDAndTaskName` in the codebase — the only references are its definition and its generated mock in `core/services/job/mocks/orm.go`; no HTTP/GraphQL/CLI handler in `core/web`, `core/web/resolver`, or `core/cmd` invokes it, and `grep` for `taskName` elsewhere only shows an unrelated local variable in `core/services/pipeline/runner.go`. This means the function currently appears to be dead/unreachable code, not wired to any unprivileged (or even privileged) request path.

### Likelihood Explanation
Because no caller path was found from an external, unprivileged (or any) API surface, the practical exploitability from an unprivileged client cannot be confirmed. If this method is later wired into a web/GraphQL handler (e.g., a "get task run result by run ID and task/dot ID" endpoint) without additional sanitization of the `taskName`/`dot_id` value, it would become directly and trivially exploitable by any authenticated user able to reach that endpoint, since dot IDs in pipeline specs can be arbitrary user-supplied strings from job DAG definitions.

### Recommendation
Convert the query to use a bound parameter instead of string interpolation:
```go
stmt := "SELECT * FROM pipeline_task_runs WHERE pipeline_run_id = $1 AND dot_id = $2;"
err := o.ds.SelectContext(ctx, &taskRuns, stmt, runID, taskName)
```
Apply the same fix pattern to any other `fmt.Sprintf`-built SQL where a non-constant value could ever be attacker-influenced (e.g., audit and lock down `findJob`'s `col` parameter to only ever accept a fixed set of literal, non-user-controlled values).

### Proof of Concept
Not exploitable via any confirmed live entry point today — no route, resolver, or CLI command was found to call `FindTaskResultByRunIDAndTaskName`. If wired up in the future, a PoC would supply `taskName = "x' OR '1'='1"` (or a UNION-based payload) to the exposed parameter, causing the interpolated SQL to become:
```sql
SELECT * FROM pipeline_task_runs WHERE pipeline_run_id = $1 AND dot_id = 'x' OR '1'='1';
```
returning arbitrary/all rows rather than the intended task run, or enabling further UNION-based data exfiltration depending on driver/type coercion.

**Caveat:** I was unable to confirm this function is reachable from any current unprivileged-actor-facing endpoint (web API, GraphQL, or gateway). The vulnerable code pattern is real and matches the CVE's bug class, but its exploitability in the current codebase is unconfirmed/likely dormant. I did not find any other SQL-injection-style string-interpolation issue in the node API authentication, session/token, external-initiator, or gateway paths — those all use parameterized queries (`$1`, `$2`, etc.), e.g. [2](#0-1) [3](#0-2) [4](#0-3) .

### Citations

**File:** core/services/job/orm.go (L1252-1260)
```go
func (o *orm) FindTaskResultByRunIDAndTaskName(ctx context.Context, runID int64, taskName string) (result []byte, err error) {
	stmt := fmt.Sprintf("SELECT * FROM pipeline_task_runs WHERE pipeline_run_id = $1 AND dot_id = '%s';", taskName)

	var taskRuns []pipeline.TaskRun
	if errB := o.ds.SelectContext(ctx, &taskRuns, stmt, runID); errB != nil {
		return nil, errB
	}
	if len(taskRuns) == 0 {
		return nil, fmt.Errorf("can't find task run with id: %v, taskName: %v", runID, taskName)
```

**File:** core/sessions/localauth/orm.go (L48-53)
```go
// FindUserByAPIToken will attempt to return an API user via the user's table token_key column.
func (o *orm) FindUserByAPIToken(ctx context.Context, apiToken string) (user sessions.User, err error) {
	sql := "SELECT * FROM users WHERE token_key = $1"
	err = o.ds.GetContext(ctx, &user, sql, apiToken)
	return
}
```

**File:** core/bridges/orm.go (L262-267)
```go
// FindExternalInitiator finds an external initiator given an authentication request
func (o *orm) FindExternalInitiator(ctx context.Context, eia *auth.Token) (*ExternalInitiator, error) {
	exi := &ExternalInitiator{}
	err := o.ds.GetContext(ctx, exi, `SELECT * FROM external_initiators WHERE access_key = $1`, eia.AccessKey)
	return exi, err
}
```

**File:** core/capabilities/vault/gw_handler.go (L180-211)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

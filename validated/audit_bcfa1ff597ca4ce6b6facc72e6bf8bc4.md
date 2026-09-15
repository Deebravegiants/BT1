[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** core/services/gateway/handlers/handler.dummy.go (L16-17)
```go
// DummyHandler forwards each request/response without doing any checks.
type dummyHandler struct {
```

**File:** core/scripts/gateway/sample_config.toml (L21-31)
```text
[ConnectionManagerConfig]
AuthGatewayId = "example_gateway"
AuthTimestampToleranceSec = 60
AuthChallengeLen = 32

[[Dons]]
DonId = "example_don"
HandlerName = "dummy"

[[Dons.Members]]
Name = "example_node"
```

**File:** SECURITY.md (L16-16)
```markdown
- Impacts on test files and configuration files, unless stated otherwise in the bug bounty program.
```

# [?] graphql: add query depth limit to prevent DoS attacks (#32344)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-08-19
Source: https://github.com/ethereum/go-ethereum/commit/1c74f2376167f50a4b7ece730c472309d7611362
Type: security-commit

## Details
graphql: add query depth limit to prevent DoS attacks (#32344)

## Summary

This PR addresses a DoS vulnerability in the GraphQL service by
implementing a maximum query depth limit. While #26026 introduced
timeout handling, it didn't fully mitigate the attack vector where
deeply nested queries can still consume excessive CPU and memory
resources before the timeout is reached.

## Changes
- Added `maxQueryDepth` constant (set to 20) to limit the maximum
nesting depth of GraphQL queries
- Applied the depth limit using `graphql.MaxDepth()` option when parsing
the schema
- Added test case `TestGraphQLMaxDepth` to verify that queries exceeding
the depth limit are properly rejected

## Security Impact

Without query depth limits, malicious actors could craft deeply nested
queries that:
  - Consume excessive CPU cycles during query parsing and execution
  - Allocate large amounts of memory for nested result structures
- Potentially cause service degradation or outages even with timeout
protection

This fix complements the existing timeout mechanism by preventing
resource-intensive queries from being executed in the first place.

## Testing

Added `TestGraphQLMaxDepth` which verifies that queries with nesting
depth > 20 are rejected with a `MaxDepthExceeded` error.

## References
  - Original issue: #26026
- Related security best practices:
https://www.howtographql.com/advanced/4-security/

---------

Co-authored-by: Felix Lange <fjl@twurst.com>

### graphql/graphql_test.go
```diff
@@ -430,6 +430,40 @@ func TestWithdrawals(t *testing.T) {
 	}
 }
 
+// TestGraphQLMaxDepth ensures that queries exceeding the configured maximum depth
+// are rejected to prevent resource exhaustion from deeply nested operations.
+func TestGraphQLMaxDepth(t *testing.T) {
+	stack := createNode(t)
+	defer stack.Close()
+
+	h, err := newHandler(stack, nil, nil, []string{}, []string{})
+	if err != nil {
+		t.Fatalf("could not create graphql service: %v", err)
+	}
+
+	var b strings.Builder
+	for i := 0; i < maxQueryDepth+1; i++ {
+		b.WriteString("ommers{")
+	}
+	b.WriteString("number")
+	for i := 0; i < maxQueryDepth+1; i++ {
+		b.WriteString("}")
+	}
+	query := fmt.Sprintf("{block{%s}}", b.String())
+
+	res := h.Schema.Exec(context.Background(), query, "", nil)
+	var found bool
+	for _, err := range res.Errors {
+		if err.Rule == "MaxDepthExceeded" {
+			found = true
+			break
+		}
+	}
+	if !found {
+		t.Fatalf("expected max depth exceeded error, got %v", res.Errors)
+	}
+}
+
 func createNode(t *testing.T) *node.Node {
 	stack, err := node.New(&node.Config{
 		HTTPHost:     "127.0.0.1",
```

### graphql/service.go
```diff
@@ -32,6 +32,9 @@ import (
 	gqlErrors "github.com/graph-gophers/graphql-go/errors"
 )
 
+// maxQueryDepth limits the maximum field nesting depth allowed in GraphQL queries.
+const maxQueryDepth = 20
+
 type handler struct {
 	Schema *graphql.Schema
 }
@@ -116,7 +119,7 @@ func New(stack *node.Node, backend ethapi.Backend, filterSystem *filters.FilterS
 func newHandler(stack *node.Node, backend ethapi.Backend, filterSystem *filters.FilterSystem, cors, vhosts []string) (*handler, error) {
 	q := Resolver{backend, filterSystem}
 
-	s, err := graphql.ParseSchema(schema, &q)
+	s, err := graphql.ParseSchema(schema, &q, graphql.MaxDepth(maxQueryDepth))
 	if err != nil {
 		return nil, err
 	}
```

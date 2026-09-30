# [?] graphql: fix an issue of nil pointer panic (#28416)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-10-26
Source: https://github.com/ethereum/go-ethereum/commit/abe3fca1deb0eca9245cccef3a9c637c57b79f7e
Type: security-commit

## Details
graphql: fix an issue of nil pointer panic (#28416)

Signed-off-by: jsvisa <delweng@gmail.com>

## Patch
### graphql/graphql.go
```diff
@@ -1325,6 +1325,9 @@ func (r *Resolver) Blocks(ctx context.Context, args struct {
 	From *Long
 	To   *Long
 }) ([]*Block, error) {
+	if args.From == nil {
+		return nil, errors.New("from block number must be specified")
+	}
 	from := rpc.BlockNumber(*args.From)
 
 	var to rpc.BlockNumber
```

### graphql/graphql_test.go
```diff
@@ -148,6 +148,11 @@ func TestGraphQLBlockSerialization(t *testing.T) {
 			want: `{"data":{"block":{"number":"0xa","call":{"data":"0x","status":"0x1"}}}}`,
 			code: 200,
 		},
+		{
+			body: `{"query": "{blocks {number}}"}`,
+			want: `{"errors":[{"message":"from block number must be specified","path":["blocks"]}],"data":null}`,
+			code: 400,
+		},
 	} {
 		resp, err := http.Post(fmt.Sprintf("%s/graphql", stack.HTTPEndpoint()), "application/json", strings.NewReader(tt.body))
 		if err != nil {
```

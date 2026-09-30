# [?] Fix panic when no params were provided when handler expects some (#726)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2023-04-12
Source: https://github.com/NethermindEth/juno/commit/974d3be4523136e9ee87726150309d22de61050c
Type: security-commit

## Details
Fix panic when no params were provided when handler expects some (#726)

## Patch
### jsonrpc/server.go
```diff
@@ -278,8 +278,12 @@ func (s *Server) handleRequest(req *request) (*response, error) {
 }
 
 func buildArguments(params, handler any, configuredParams []Parameter) ([]reflect.Value, error) {
-	var args []reflect.Value
+	args := make([]reflect.Value, 0, len(configuredParams))
 	if isNil(params) {
+		if len(configuredParams) > 0 {
+			return nil, errors.New("missing non-optional param field")
+		}
+
 		return args, nil
 	}
 
@@ -314,7 +318,6 @@ func buildArguments(params, handler any, configuredParams []Parameter) ([]reflec
 			}
 			args = append(args, v)
 		}
-		return args, nil
 	case reflect.Map:
 		paramsMap := params.(map[string]any)
 
@@ -335,9 +338,9 @@ func buildArguments(params, handler any, configuredParams []Parameter) ([]reflec
 
 			args = append(args, v)
 		}
-		return args, nil
 	default:
 		// Todo: consider returning InternalError
 		return nil, errors.New("impossible param type: check request.isSane")
 	}
+	return args, nil
 }
```

### jsonrpc/server_test.go
```diff
@@ -128,6 +128,10 @@ func TestHandle(t *testing.T) {
 			req: `{"jsonrpc" : "2.0", "method" : "doesnotexits" , "id" : 2}`,
 			res: `{"jsonrpc":"2.0","error":{"code":-32601,"message":"Method Not Found"},"id":2}`,
 		},
+		"no params": {
+			req: `{"jsonrpc" : "2.0", "method" : "method", "id" : 5}`,
+			res: `{"jsonrpc":"2.0","error":{"code":-32602,"message":"Invalid Params","data":"missing non-optional param field"},"id":5}`,
+		},
 		"missing param(s)": {
 			req: `{"jsonrpc" : "2.0", "method" : "method", "params" : [3, false] , "id" : 3}`,
 			res: `{"jsonrpc":"2.0","error":{"code":-32602,"message":"Invalid Params","data":"missing/unexpected params in list"},"id":3}`,
```

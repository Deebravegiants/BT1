# [?] fix logging without raise panic

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-06-10
Source: https://github.com/0xsoniclabs/sonic/commit/5569826effa9c2381ab78da32160ed2957ca15e7
Type: security-commit

## Details
fix logging without raise panic

## Patch
### src/metrics/metrics.go
```diff
@@ -6,8 +6,6 @@ import (
 	"sync"
 	"time"
 
-	"github.com/pkg/errors"
-
 	"github.com/Fantom-foundation/go-lachesis/src/logger"
 )
 
@@ -31,7 +29,7 @@ func init() {
 		case "0", "false", "off":
 			Enabled = false
 		default:
-			panic(errors.Errorf("incorrect value in '%s'", envEnabled))
+			log.Errorf("incorrect value in '%s'", envEnabled)
 		}
 	}
 }
```

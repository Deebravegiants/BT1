# [?] fix(relayer): crash on RabbitMQ subscription retry exhaustion instead of zombieing (#21731)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-05-28
Source: https://github.com/taikoxyz/taiko-mono/commit/7a685cc5f1e7ddf4f8e4484061a527ac9858a21a
Type: security-commit

## Details
fix(relayer): crash on RabbitMQ subscription retry exhaustion instead of zombieing (#21731)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### packages/relayer/processor/processor.go
```diff
@@ -8,6 +8,7 @@ import (
 	"fmt"
 	"log/slog"
 	"math/big"
+	"os"
 	"strings"
 	"sync"
 	"time"
@@ -374,7 +375,8 @@ func (p *Processor) Start() error {
 
 			return nil
 		}, bo); err != nil {
-			slog.Error("rabbitmq subscribe backoff retry error", "err", err.Error())
+			slog.Error("rabbitmq subscribe backoff retry error, exiting so container restarts", "err", err.Error())
+			os.Exit(1)
 		}
 	}()
 
```

### packages/relayer/watchdog/watchdog.go
```diff
@@ -8,6 +8,7 @@ import (
 	"fmt"
 	"log/slog"
 	"math/big"
+	"os"
 	"sync"
 	"time"
 
@@ -239,7 +240,8 @@ func (w *Watchdog) Start() error {
 
 			return nil
 		}, bo); err != nil {
-			slog.Error("rabbitmq subscribe backoff retry error", "err", err.Error())
+			slog.Error("rabbitmq subscribe backoff retry error, exiting so container restarts", "err", err.Error())
+			os.Exit(1)
 		}
 	}()
 
```

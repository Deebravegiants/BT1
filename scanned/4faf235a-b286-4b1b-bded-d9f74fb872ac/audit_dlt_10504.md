# [?] Merge branch 'master' into fix-stopandwait-deadlock

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-07
Source: https://github.com/OffchainLabs/nitro/commit/9eda7a0867156407adf256211eea015abad5f651
Type: security-commit

## Details
Merge branch 'master' into fix-stopandwait-deadlock

## Patch
### arbnode/seq_coordinator.go
```diff
@@ -9,7 +9,9 @@ import (
 	"encoding/json"
 	"errors"
 	"fmt"
+	"net"
 	"net/http"
+	"net/url"
 	"sync"
 	"sync/atomic"
 	"time"
@@ -896,6 +898,33 @@ func (c *SeqCoordinator) Start(ctxIn context.Context) {
 	if c.config.ChosenHealthcheckAddr != "" {
 		c.StopWaiter.LaunchThread(c.launchHealthcheckServer)
 	}
+	// Verifies that c.config.MyUrl is valid and is in the priorities list in redis
+	if c.config.Url() == redisutil.INVALID_URL {
+		return // skip if used for read access only
+	}
+	priorities, err := c.RedisCoordinator().GetPriorities(ctxIn)
+	if err != nil {
+		log.Error("Error fetching priorities list from redis during start up", "err", err)
+		return
+	}
+	for _, addr := range priorities {
+		if addr == c.config.MyUrl {
+			// Validate c.config.MyUrl by connecting to self
+			parsedURL, err := url.Parse(addr)
+			if err != nil {
+				log.Error("Failed to parse --node.seq-coordinator.my-url", "myUrl", addr, "err", err)
+				return
+			}
+			conn, err := net.DialTimeout("tcp", parsedURL.Host, 5*time.Second)
+			if err != nil {
+				log.Error("Failed to connect to sequencer's url specified in --node.seq-coordinator.my-url", "myUrl", addr, "err", err)
+			} else {
+				conn.Close()
+			}
+			return
+		}
+	}
+	log.Error("Sequencer did not find its URL in the priorities list in redis", "myUrl", c.config.MyUrl)
 }
 
 func (c *SeqCoordinator) chooseRedisAndUpdate(ctx context.Context, newRedisCoordinator *redisutil.RedisCoordinator) time.Duration {
```

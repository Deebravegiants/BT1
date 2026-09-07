# [M] rclone: Infinite Scale TUS Creation Transport Error Causes a Nil-Response Panic

## Summary
Severity: Medium
Advisory: GHSA-3x6r-wxxg-53vv
CWE: CWE-248, CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-3x6r-wxxg-53vv
Type: github-advisory

## Affected
- Go: `github.com/rclone/rclone` — affected >=0 <1.75.0

## Details
## 1. Summary

A transport failure during the initial Infinite Scale TUS creation POST can return `(nil response, non-nil error)`. Rclone dereferences the nil response before processing the error and panics. The production `CreateUploader` path reproduced the crash against a closed endpoint.

The security case is deployment-dependent. A one-shot upload already fails when its endpoint resets, while RC jobs recover panics in `fs/rc/jobs/job.go` and return a job error. The incremental denial of service is strongest in a long-lived VFS mount or concurrent/multi-remote CLI process where the upload runs in an unrecovered goroutine and the panic terminates unrelated work.

## 2. Affected Assets & Attack Surface

- Verified rclone revision: `a0c09f1381ae93e2a9a33c529d170186c61ad058` (`v1.74.0-240-ga0c09f138`)
- Current-master check: `backend/webdav/tus.go` was unchanged at master commit `961266888fe797390c535386f3b3aa46f4853602` on 2026-07-18
- Response evaluation: `backend/webdav/tus.go:45-59`
- Creation path: `backend/webdav/tus.go:61-107`
- Unrecovered VFS caller: `vfs/write.go:71-81`
- Contained RC caller: `fs/rc/jobs/job.go:107-115`
- Configuration: Infinite Scale WebDAV uploads using TUS
- Code triggers: any pre-response transport failure, including refusal, reset, timeout, DNS/TLS/proxy failure, or cancellation
- Security trigger: a malicious/compromised configured endpoint resets an upload in a long-lived or multi-workload process

## 3. Technical Root Cause Analysis

`getTusLocationOrRetry` switches on `resp.StatusCode` before checking whether `resp` is nil or handling the accompanying error. A nil response is valid when the HTTP transaction fails before a response is parsed. There is no recovery boundary in the WebDAV operation itself. Whether the panic is process-fatal depends on its caller: the VFS write path starts `operations.Rcat` in an unrecovered goroutine (`vfs/write.go:71-81`), whereas RC jobs wrap their function in `recover` (`fs/rc/jobs/job.go:107-115`).

## 4. Proof-of-Concept & Evidence

1. Configure the actual Infinite Scale creation path to a closed local endpoint.
2. Invoke `Object.CreateUploader`.
3. The POST returns a transport error and no response.
4. `getTusLocationOrRetry` dereferences `resp.StatusCode` and panics.

A remote endpoint can produce the same `(nil response, non-nil error)` state by accepting and resetting the connection before returning an HTTP response. TLS prevents arbitrary response modification but does not prevent the configured endpoint from closing or resetting its own connection. Refusal, DNS, TLS, proxy, and cancellation failures exercise the code defect but do not by themselves identify a remote security actor.

## 5. Impact Assessment

In an unrecovered CLI or VFS upload goroutine, the panic terminates the rclone process and any unrelated work it hosts. A hostile configured endpoint can repeat the condition whenever the victim initiates a TUS upload. RC jobs are excluded from the process-wide impact because their execution boundary recovers the panic and records an error. In a one-shot process dedicated to the hostile endpoint, the incremental security impact over an ordinary transport error is limited.

## 6. Remediation Guidance

- Check `resp == nil` before accessing response fields.
- Pass transport errors through the existing retry policy and return a normal error after exhaustion.
- Test refusal, reset, timeout, DNS, TLS, proxy, and cancellation paths.
- Add panic containment to long-lived worker goroutines as defense in depth; keep nil handling as the primary fix.

## References
- https://github.com/rclone/rclone/security/advisories/GHSA-3x6r-wxxg-53vv
- https://github.com/rclone/rclone/commit/5871d98c368751a6d992ed64f8cd22cb78c44cee
- https://github.com/rclone/rclone
- https://github.com/rclone/rclone/releases/tag/v1.75.0

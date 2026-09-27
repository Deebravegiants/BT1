# [H] The Eclipse Jetty Server Artifact has a Gzip request memory leak 

## Summary
Severity: High
Advisory: GHSA-xxh7-fcf3-rj7f
CVE: CVE-2026-1605
CWE: CWE-400, CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-xxh7-fcf3-rj7f
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.1.0 <12.1.6
- Maven: `org.eclipse.jetty:jetty-server` — affected >=12.0.0 <12.0.32

## Details
### Description (as reported)

There is a memory leak when using `GzipHandler` in jetty-12.0.30 that can cause off-heap OOMs. This can be used for DoS attacks so I'm reporting this as a vulnerability.

The leak is created by requests where the request is inflated (`Content-Encoding: gzip`) and the response is not deflated (no `Accept-Encoding: gzip`). In these conditions, a new inflator will be created by `GzipRequest` and never released back into `GzipRequest.__inflaterPool` because `gzipRequest.destory()` is not called.

In heap dumps one can see thousands of `java.util.zip.Inflator` objects, which use both Java heaps and native memory. Leaking native memory causes of off-heap OOMs.

Code path in `GzipHandler.handle()`:
1. Line 601: `GzipRequest` is created when request inflation is needed.
2. Lines 611-616: The callback is only wrapped in `GzipResponseAndCallback` when both inflation and deflation are needed.
3. Lines 619-625: If the handler accepts the request (returns true), `gzipRequest.destroy()` is only called in the "request not accepted" path (returns false)

When deflation is needed, `GzipResponseAndCallback` (lines 102 and 116) properly calls `gzipRequest.destroy()` in its `succeeded()` and `failed()` methods. But this wrapper is only created when deflation is needed.

Possible fix:
The callback should be wrapped whenever a `GzipRequest` is created, not just when deflation is needed. This ensures `gzipRequest.destroy()` is always called when the request completes.


### Impact
The leak causes the JVM to crash with OOME.

### Patches
No patches yet.

### Workarounds
Disable `GzipHandler`.

### References
https://github.com/jetty/jetty.project/issues/14260

https://gitlab.eclipse.org/security/cve-assignment/-/issues/79

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-xxh7-fcf3-rj7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-1605
- https://github.com/jetty/jetty.project/issues/14260
- https://github.com/jetty/jetty.project
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/79

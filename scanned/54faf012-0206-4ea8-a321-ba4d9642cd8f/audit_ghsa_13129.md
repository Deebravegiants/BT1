# [H] Privilege Escalation on Linux/MacOS

## Summary
Severity: High
Advisory: GHSA-2pxw-r47w-4p8c
CVE: CVE-2023-28434
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2023-09-05
Source: https://github.com/advisories/GHSA-2pxw-r47w-4p8c
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0 <0.0.0-202303200415

## Details
### Impact
An attacker can use crafted requests to bypass metadata bucket name checking and put an object into any bucket while processing `PostPolicyBucket`. To carry out this attack, the attacker requires credentials with `arn:aws:s3:::*` permission, as well as enabled Console API access.

### Patches
```
commit 67f4ba154a27a1b06e48bfabda38355a010dfca5
Author: Aditya Manthramurthy <donatello@users.noreply.github.com>
Date:   Sun Mar 19 21:15:20 2023 -0700

    fix: post policy request security bypass (#16849)
```

### Workarounds
Browser API access must be enabled turning off `MINIO_BROWSER=off` allows for this workaround.

### References
The vulnerable code:
```go
// minio/cmd/generic-handlers.go
func setRequestValidityHandler(h http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    // ...
    // For all other requests reject access to reserved buckets
    bucketName, _ := request2BucketObjectName(r)
    if isMinioReservedBucket(bucketName) || isMinioMetaBucket(bucketName) {
      if !guessIsRPCReq(r) && !guessIsBrowserReq(r) && !guessIsHealthCheckReq(r) && !guessIsMetricsReq(r) && !isAdminReq(r) && !isKMSReq(r) {
        if ok {
          tc.FuncName = "handler.ValidRequest"
          tc.ResponseRecorder.LogErrBody = true
        }
        writeErrorResponse(r.Context(), w, errorCodes.ToAPIErr(ErrAllAccessDisabled), r.URL)
        return
      }
    }
    // ...
```

## References
- https://github.com/minio/minio/security/advisories/GHSA-2pxw-r47w-4p8c
- https://nvd.nist.gov/vuln/detail/CVE-2023-28434
- https://github.com/minio/minio/pull/16849
- https://github.com/minio/minio/commit/67f4ba154a27a1b06e48bfabda38355a010dfca5
- https://github.com/minio/minio
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-28434

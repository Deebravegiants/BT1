# [M] MinIO information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-95fr-cm4m-q5p9
CVE: CVE-2024-36107
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-95fr-cm4m-q5p9
Type: github-advisory

## Affected
- Go: `github.com/minio/minio` — affected >=0 <0.0.0-20240527191746-e0fe7cc39172

## Details
### Impact
[If-Modified-Since](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since)
[If-Unmodified-Since](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Unmodified-Since) 

Headers when used with anonymous requests by sending a random object name requests you can figure
out if the object exists or not on the server on a specific bucket and also gain access to some amount of
information such as  

```
Last-Modified (of the latest version)
Etag (of the latest version) 
x-amz-version-id (of the latest version)
Expires (metadata value of the latest version)
Cache-Control (metadata value of the latest version)
```

This conditional check was being honored before validating if the anonymous
access is indeed allowed on the metadata of an object.

### Patches
Yes this issue has been already fixed in 

```
commit e0fe7cc391724fc5baa85b45508f425020fe4272 (HEAD -> master, origin/master)
Author: Harshavardhana <harsha@minio.io>
Date:   Mon May 27 12:17:46 2024 -0700

    fix: information disclosure bug in preconditions GET (#19810)
    
    precondition check was being honored before, validating
    if anonymous access is allowed on the metadata of an
    object, leading to metadata disclosure of the following
    headers.
    
    ```
    Last-Modified
    Etag
    x-amz-version-id
    Expires:
    Cache-Control:
    ```
    
    although the information presented is minimal in nature,
    and of opaque nature. It still simply discloses that an
    object by a specific name exists or not without even having
    enough permissions.
```

Users must upgrade to RELEASE.2024-05-27T19-17-46Z for the fix

### Workarounds
There are no workarounds.

### References
Refer to the pull request #19810 for more information on the fix.

## References
- https://github.com/minio/minio/security/advisories/GHSA-95fr-cm4m-q5p9
- https://nvd.nist.gov/vuln/detail/CVE-2024-36107
- https://github.com/minio/minio/pull/19810
- https://github.com/minio/minio/commit/e0fe7cc391724fc5baa85b45508f425020fe4272
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Unmodified-Since
- https://github.com/minio/minio

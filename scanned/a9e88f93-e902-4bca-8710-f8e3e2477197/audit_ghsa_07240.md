# [M] OpenList: Search metadata/count disclosure via Non-Separator-Aware Path Check in Bleve Search

## Summary
Severity: Medium
Advisory: GHSA-p6ph-3jx2-3337
CWE: CWE-200, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-p6ph-3jx2-3337
Type: github-advisory

## Affected
- Go: `github.com/OpenListTeam/OpenList/v4` — affected >=0 <4.2.4

## Details
### Summary
An authorization bypass and information disclosure vulnerability exists in the search API of `Openlist`. Due to a non-separator-aware path check and unfiltered backend counting, a low-privileged user can bypass their assigned `BasePath` restrictions to discover and access metadata of files residing in unauthorized sibling directories.

### Details
This vulnerability stems from two combined logic flaws when the `bleve` search engine is utilized:

1. **Insecure Path Prefix Validation:** In the search handler (`server/handles/search.go`), the application attempts to restrict search results to the user's allowed namespace using a simple prefix check: `strings.HasPrefix(node.Parent, user.BasePath)`. Because this function is not path-separator aware, a user with a `BasePath` restricted to `/base` will successfully pass the authorization check for a completely separate directory named `/base2` (since "/base2" starts with "/base").

2. **Unfiltered Total Count Leakage:** The `bleve` backend (`internal/search/bleve/search.go`) searches the index globally and ignores the `req.Parent` boundary. Even if the application later successfully filters out unauthorized items from the `Content` array (e.g., via `CanAccess` meta password checks), it still returns the raw `Total` count provided by the search backend. This allows an attacker to perform blind data-enumeration, confirming the existence of sensitive files outside their namespace by observing the `Total` count.

### PoC
**Prerequisites:**
1. Log in as an administrator and set the Search Index Mode to `bleve`. Build the index.
2. Create two directories at the root level: `/base` and `/base2`.
3. Upload a sensitive file into the unauthorized directory: `/base2/secret_financial_report.pdf`.
4. Create a low-privileged test user and strictly set their `Base path` to `/base`.

**Exploitation Steps:**
1. Authenticate as the newly created low-privileged user.
2. Send the following HTTP request to the search API:
```http
POST /api/fs/search HTTP/1.1
Host: <your-openlist-host>
Authorization: <test-user-token>
Content-Type: application/json

{
  "parent": "/",
  "keywords": "secret",
  "page": 1,
  "per_page": 20,
  "scope": 0
}
```
3. Observe the response: Due to the prefix bypass (`strings.HasPrefix("/base2", "/base") == true`), the metadata for `secret_financial_report.pdf` will be leaked in the response Content.
    - Alternatively, even if access is further blocked by folder-level passwords, the Total field will return > 0, allowing the attacker to blindly confirm the existence of the keyword "secret" in unauthorized global directories.
 
<img width="2112" height="1381" alt="image" src="https://github.com/user-attachments/assets/9f8c5e18-8744-4363-8d3f-5e6cf691f061" />

### Impact
This is an Information Disclosure and Horizontal/Vertical Privilege Escalation vulnerability. Any authenticated user can enumerate hidden infrastructure, verify the existence of sensitive files (e.g., passwords, internal documents), and extract file metadata across the entire storage namespace, completely defeating the BasePath isolation mechanism.

### Remediation Recommendations
1. Separator-Aware Path Containment: Replace strings.HasPrefix with a robust path containment check. For example: target == base || strings.HasPrefix(target, base + "/"), or use a dedicated utility like utils.IsSubPath().
2. Backend-Level Filtering: Enforce the path boundary within the bleve query itself (e.g., using indexed parent path hashes) rather than relying solely on post-query API filtering.
3. Accurate Total Calculation: Compute the Total count only after all authorization and path filters have been applied to the result set.

## References
- https://github.com/OpenListTeam/OpenList/security/advisories/GHSA-p6ph-3jx2-3337
- https://github.com/OpenListTeam/OpenList/commit/59bd3431408578f420895457554700cc9a52375a
- https://github.com/OpenListTeam/OpenList/commit/84ecda35aae2bd0020474086e6ddfd3aa2340679
- https://github.com/OpenListTeam/OpenList
- https://github.com/OpenListTeam/OpenList/releases/tag/v4.2.4

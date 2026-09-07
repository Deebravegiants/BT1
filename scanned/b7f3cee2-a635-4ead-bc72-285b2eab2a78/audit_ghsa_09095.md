# [H] @tdurieux/anonymous_github Vulnerable to XSS via Unsanitized GitHub Repository Content Rendering in Anonymous GitHub Origin

## Summary
Severity: High
Advisory: GHSA-g485-8j3v-p6x8
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-g485-8j3v-p6x8
Type: github-advisory

## Affected
- npm: `@tdurieux/anonymous_github` — affected >=2.2.0 <2.3.0

## Details
### Summary

Anonymous GitHub fetches repository content (e.g., markdown files) from GitHub's API and renders it without sanitization. On the client side, markdown is parsed with `marked` (with `sanitize: false`) and injected into the DOM via `$sce.trustAsHtml()` + `ng-bind-html`, bypassing AngularJS's built-in XSS protection. An attacker can craft a malicious GitHub repository whose README executes arbitrary JavaScript in the Anonymous GitHub origin.

### Details

#### README fetched from GitHub API

The server fetches the README via GitHub's REST API and stores the raw markdown in MongoDB:

```typescript
// https://github.com/tdurieux/anonymous_github/blob/b2d77faa6c6f35ad9ae6ed46e3a3fa4681ac84c2/src/core/source/GitHubRepository.ts#L162-L174
const ghRes = await oct.repos.getReadme({
  owner: this.owner,
  repo: this.repo,
  ref: selected?.commit,
});
const readme = Buffer.from(
  ghRes.data.content,
  ghRes.data.encoding as BufferEncoding
).toString("utf-8");
selected.readme = readme;
await model.save();
```

It is then served to the client with no sanitization:

```typescript
// https://github.com/tdurieux/anonymous_github/blob/b2d77faa6c6f35ad9ae6ed46e3a3fa4681ac84c2/src/server/routes/repository-private.ts#L254-L260
return res.send(
  await repo.readme({
    accessToken: token,
    force: req.query.force == "1",
    branch: req.query.branch as string,
  })
);
```

#### Client-side rendering via `$sce.trustAsHtml()` + `ng-bind-html`

The client fetches the raw README, parses it with `renderMD()` (which uses `marked` with `sanitize: false`), then bypasses AngularJS sanitization:

```javascript
// https://github.com/tdurieux/anonymous_github/blob/b2d77faa6c6f35ad9ae6ed46e3a3fa4681ac84c2/public/script/app.js#L1219-L1226
const res = await $http.get(`/api/repo/${o.owner}/${o.repo}/readme`, {
  params: { force: force === true ? "1" : "0", branch: $scope.source.branch },
});
$scope.readme = res.data;
```

```javascript
// https://github.com/tdurieux/anonymous_github/blob/b2d77faa6c6f35ad9ae6ed46e3a3fa4681ac84c2/public/script/app.js#L1339-L1343
const html = renderMD(
  $scope.anonymize_readme,
  `https://github.com/${o.owner}/${o.repo}/raw/${$scope.source.branch}/`
);
$scope.html_readme = $sce.trustAsHtml(html);  // sink: bypasses Angular XSS protection
```

The `renderMD()` function explicitly disables sanitization:

```javascript
// https://github.com/tdurieux/anonymous_github/blob/b2d77faa6c6f35ad9ae6ed46e3a3fa4681ac84c2/public/script/utils.js#L165-L176
marked.setOptions({
  sanitize: false,  // HTML in markdown is preserved as-is
  // ...
});
return marked.parse(md, { renderer });
```

The resulting HTML is bound to the DOM via `ng-bind-html`, which trusts the string marked by `$sce.trustAsHtml()` and inserts it as innerHTML.

### Impact

1. **Stored XSS**: Any malicious GitHub repository can execute JavaScript in the Anonymous GitHub origin when a user anonymizes it or views its content
2. **Account Takeover**: Steal authentication tokens and session cookies
3. **Data Exfiltration**: Access other users' anonymization configurations and private repository data via `/api/user` and `/api/repo/list`

### Proof of Concept

![poc-xss-anonymous-github](https://github.com/user-attachments/assets/c1bf3ed9-4e1e-4c8e-87f0-782a8d5f6ead)

1. Create a GitHub repository with a malicious `README.md`:

```markdown
# Innocent README
<img src=x onerror="alert(document.domain)">
```

2. On Anonymous GitHub, enter the malicious repository URL to anonymize it
3. The XSS executes immediately when the README preview is rendered on the anonymize page

### Remediation

1. Sanitize markdown output with DOMPurify before rendering (the dependency already exists but is unused)
2. Serve HTML files with `Content-Disposition: attachment` or in a sandboxed iframe on a separate origin
3. Replace `$sce.trustAsHtml()` with proper `ngSanitize` usage
4. HTML-escape filenames and paths in directory listing templates
5. Add Content Security Policy headers

### Credits

Zhengyu Liu, Jingcheng Yang

## References
- https://github.com/tdurieux/anonymous_github/security/advisories/GHSA-g485-8j3v-p6x8
- https://github.com/tdurieux/anonymous_github

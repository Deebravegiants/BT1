# [H] OneUptime has broken access control in GitHub App installation flow that allows unauthorized project binding

## Summary
Severity: High
Advisory: GHSA-656w-6f6c-m9r6
CVE: CVE-2026-30920
CWE: CWE-345, CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-656w-6f6c-m9r6
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <10.0.19

## Details
### Summary

OneUptime's GitHub App callback trusts attacker-controlled `state` and `installation_id` values and updates `Project.gitHubAppInstallationId` with `isRoot: true` without validating that the caller is authorized for the target project. This allows an attacker to overwrite another project's GitHub App installation binding.

Related GitHub endpoints also lack effective authorization, so a valid installation ID can be used to enumerate repositories and create `CodeRepository` records in an arbitrary project.

### Details

The callback decodes unsigned base64 JSON from `state` and uses the embedded `projectId` directly:

- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L34-L112

It then writes the supplied `installation_id` into the target project with root privileges:

```ts
await ProjectService.updateOneById({
  id: new ObjectID(projectId),
  data: { gitHubAppInstallationId: installationId },
  props: { isRoot: true },
});
```

The `userId` in `state` is only checked for presence, not authenticity:

- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L73-L79

The install flow also generates `state` as plain base64 JSON, not a signed or session-bound token:

- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L127-L165

The follow-on endpoints are also vulnerable:

- Repository listing: https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L179-L258
- Repository connect: https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L260-L356
- Middleware allows requests with no token to continue as `Public`: https://github.com/OneUptime/oneuptime/blob/master/Common/Server/Middleware/UserAuthorization.ts#L205-L211
- Installation tokens are minted from any valid installation ID: https://github.com/OneUptime/oneuptime/blob/master/Common/Server/Utils/CodeRepository/GitHub/GitHub.ts#L347-L425

### PoC

Minimal proof of unauthorized project tampering:

```bash
STATE=$(printf '%s' '{"projectId":"<victim-project-uuid>","userId":"x"}' | base64 | tr -d '\n')
curl -isk "https://<host>/api/github/auth/callback?installation_id=999999999&state=${STATE}"
```

Expected result:

- Server returns a `302` redirect to `/dashboard/<victim-project-uuid>/code-repository?installation_id=999999999`
- The target project's `gitHubAppInstallationId` is overwritten

### Impact

- Unauthorized modification of `Project.gitHubAppInstallationId`
- Temporary GitHub integration breakage if a bogus installation ID is set
- Cross-project binding of attacker-controlled GitHub App installations
- Repository metadata disclosure for a supplied valid installation ID
- Unauthorized creation of `CodeRepository` records in arbitrary projects

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-656w-6f6c-m9r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30920
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L127-L165
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L179-L258
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L260-L356
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L34-L112
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/API/GitHubAPI.ts#L73-L79
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/Middleware/UserAuthorization.ts#L205-L211
- https://github.com/OneUptime/oneuptime/blob/master/Common/Server/Utils/CodeRepository/GitHub/GitHub.ts#L347-L425

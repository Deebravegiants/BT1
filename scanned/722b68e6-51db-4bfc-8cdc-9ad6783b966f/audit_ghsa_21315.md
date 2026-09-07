# [M] Team scope authorization bypass when Post/Put request with :team_name in body, allows HTTP parameter pollution 

## Summary
Severity: Medium
Advisory: GHSA-5jp2-vwrj-99rf
CVE: CVE-2022-31683
CWE: CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-5jp2-vwrj-99rf
Type: github-advisory

## Affected
- Go: `github.com/concourse/concourse` — affected >=0 <6.7.9
- Go: `github.com/concourse/concourse` — affected >=7.0.0 <7.8.3

## Details
### Impact
For some Post/Put Concourse endpoint containing `:team_name` in the URL, a Concourse user can send a request with body including `:team_name=team2` to bypass team scope check to gain access to certain resources belong to any other team. The user only needs a valid user session and belongs to team2.

Exploitable endpoints:
```
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/jobs/:job_name/builds/:build_name", Method: "POST", Name: RerunJobBuild},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/jobs/:job_name/pause", Method: "PUT", Name: PauseJob},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/jobs/:job_name/unpause", Method: "PUT", Name: UnpauseJob},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/jobs/:job_name/schedule", Method: "PUT", Name: ScheduleJob},

{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/pause", Method: "PUT", Name: PausePipeline},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/unpause", Method: "PUT", Name: UnpausePipeline},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/expose", Method: "PUT", Name: ExposePipeline},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/hide", Method: "PUT", Name: HidePipeline},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/rename", Method: "PUT", Name: RenamePipeline},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/archive", Method: "PUT", Name: ArchivePipeline},

{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/resources/:resource_name/versions/:resource_config_version_id/enable", Method: "PUT", Name: EnableResourceVersion},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/resources/:resource_name/versions/:resource_config_version_id/disable", Method: "PUT", Name: DisableResourceVersion},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/resources/:resource_name/versions/:resource_config_version_id/pin", Method: "PUT", Name: PinResourceVersion},
{Path: "/api/v1/teams/:team_name/pipelines/:pipeline_name/resources/:resource_name/unpin", Method: "PUT", Name: UnpinResource},
	
{Path: "/api/v1/teams/:team_name/artifacts", Method: "POST", Name: CreateArtifact},
```

### Steps to reproduce

1. Set up a Concourse deployment with team 1 (with pipeline 1) and team 2. User is in team 2 but not team 1.
2. Login as user to team 2.
```
fly -t ci login -n team2 -u user -p password
```
3. Try pausing pipeline 1 in team 1 using fly. Verify the command output is `pipeline 'pipeline1' not found`.
```
fly -t ci pause-pipeline -p pipeline1
```


4. Send a customized request through `fly curl` command intend to pause pipeline 1 again. 
```
fly -t ci curl /api/v1/teams/team1/pipelines/pipeline1/pause -- -X PUT -d ":team_name=team2" -H "Content-type: application/x-www-form-urlencoded"
```
5. pipeline 1 in team 1 will be paused.

In step 4, the parameter pollution would allow an user from any team to pause a pipeline that belongs to other team.

### Patches
Concourse [v6.7.9](https://github.com/concourse/concourse/releases/tag/v6.7.9) and [v7.8.3](https://github.com/concourse/concourse/releases/tag/v7.8.3) were both released with a fix on October 12, 2022.

Instead of using [`FormValue`](https://pkg.go.dev/net/http#Request.FormValue) to parse team_name in the request, where allows body parameters to take precedence over URL query string values, both patch versions are now using `URL.Query().Get()` over multiple scope handlers to prevent the parameter pollution.

### Workarounds
No known workarounds for existing versions.

### References
 * https://github.com/concourse/concourse/pull/8566: PR with the fix

### For more information
If you have any questions or comments about this advisory, you may reach us privately at [security@concourse-ci.org](mailto:security@concourse-ci.org).

## References
- https://github.com/concourse/concourse/security/advisories/GHSA-5jp2-vwrj-99rf
- https://nvd.nist.gov/vuln/detail/CVE-2022-31683
- https://github.com/concourse/concourse/pull/8566
- https://github.com/concourse/concourse/pull/8580
- https://github.com/concourse/concourse/commit/57e06711b0d861775a5a6bd078a34abeb0e2638e
- https://github.com/concourse/concourse/commit/ba885834d9bcbb9d1ccb9964faa7af0e78a72205
- https://github.com/concourse/concourse
- https://github.com/concourse/concourse/releases/tag/v6.7.9
- https://github.com/concourse/concourse/releases/tag/v7.8.3

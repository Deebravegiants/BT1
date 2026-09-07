# [M] Harbor timing attack risk

## Summary
Severity: Medium
Advisory: GHSA-mq6f-5xh5-hgcf
CVE: CVE-2023-20902
CWE: CWE-208, CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-mq6f-5xh5-hgcf
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=0 <1.10.18
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.7.3
- Go: `github.com/goharbor/harbor` — affected >=2.8.0 <2.8.3

## Details
In the Harbor jobservice container, the comparison of secrets in the authenticator type is prone to timing attacks. The vulnerability occurs due to the following code: https://github.com/goharbor/harbor/blob/aaea068cceb4063ab89313d9785f2b40f35b0d63/src/jobservice/api/authenticator.go#L69-L69
To avoid this issue, constant time comparison should be used.
```
subtle.ConstantTimeCompare([]byte(expectedSecret), []byte(secret)) == 0
```

### Impact
This attack might be possible theoretically, but no workable proof of concept is available, and access complexity is set at High.
The jobservice exposes these APIs
```
Create a job task --- POST /api/v1/jobs    
Get job task information --- GET /api/v1/jobs/{job_id}
Stop job task ---  POST /api/v1/jobs/{job_id}
Get job log task ---  GET /api/v1/jobs/{job_id}/log
Get job execution --- GET /api/v1/jobs/{job_id}/executions
Get job stats ---  GET /api/v1/stats
Get job service configuration ---  GET /api/v1/config
```
It is used to create jobs/stop job tasks and retrieve job task information.  If an attacker obtains the secrets, it is possible to retrieve the job information, create a job, or stop a job task. 

The following versions of Harbor are involved:
<=Harbor 2.8.2, <=Harbor 2.7.2, <= Harbor 2.6.x, <=Harbor 1.10.17


### Patches
Harbor 2.8.3, Harbor 2.7.3, Harbor 1.10.18

### Workarounds
Because the jobservice only exposes HTTP service to harbor-core containers, blocking any inbound traffic from the external network to the jobservice container can reduce the risk.

### Credits
Thanks to Porcupiney Hairs for reporting this issue.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-mq6f-5xh5-hgcf
- https://nvd.nist.gov/vuln/detail/CVE-2023-20902
- https://github.com/goharbor/harbor
- https://github.com/goharbor/harbor/blob/aaea068cceb4063ab89313d9785f2b40f35b0d63/src/jobservice/api/authenticator.go#L69-L69
- https://github.com/goharbor/harbor/releases/tag/v1.10.18
- https://github.com/goharbor/harbor/releases/tag/v2.7.3
- https://github.com/goharbor/harbor/releases/tag/v2.8.3

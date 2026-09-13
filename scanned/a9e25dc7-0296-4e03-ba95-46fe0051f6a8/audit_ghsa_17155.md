# [C] Bypassing Brute Force Protection via Application Crash and In-Memory Data Loss

## Summary
Severity: Critical
Advisory: GHSA-x32m-mvfj-52xv
CVE: CVE-2024-21652
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-x32m-mvfj-52xv
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.8.13
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.9.0 <2.9.9
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.10.0 <2.10.4

## Details
### Summary
An attacker can exploit a chain of vulnerabilities, including a Denial of Service (DoS) flaw and in-memory data storage weakness, to effectively bypass the application's brute force login protection. This makes the application susceptible to brute force attacks, compromising the security of all user accounts.

### Details
The issue arises from two main vulnerabilities:

1. The application crashes due to a previously described DoS vulnerability caused by unsafe array modifications in a multi-threaded environment.
2. The application saves the data of failed login attempts in-memory, without persistent storage. When the application crashes and restarts, this data is lost, resetting the brute force protections.

```go
// LoginAttempts is a timestamped counter for failed login attempts

type LoginAttempts struct {  
// Time of the last failed login LastFailed time.Time `json:"lastFailed"` // Number of consecutive login failures FailCount int `json:"failCount"`

}
```

By chaining these vulnerabilities, an attacker can circumvent the limitations placed on the number of login attempts.

### PoC
1. Run the provided PoC script.
2. Observe that the script makes 6 login attempts, one more than the set limit of 5 failed attempts.
3. This is made possible because the script triggers a server restart via the DoS vulnerability after 5 failed attempts, thus resetting the counter for failed login attempts.

### Impact
This is a critical security vulnerability that allows attackers to bypass the brute force login protection mechanism. Not only can they crash the service affecting all users, but they can also make unlimited login attempts, increasing the risk of account compromise.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-x32m-mvfj-52xv
- https://nvd.nist.gov/vuln/detail/CVE-2024-21652
- https://github.com/argoproj/argo-cd/commit/17b0df1168a4c535f6f37e95f25ed7cd81e1fa4d
- https://github.com/argoproj/argo-cd/commit/6e181d72b31522f886a2afa029d5b26d7912ec7b
- https://github.com/argoproj/argo-cd/commit/cebb6538f7944c87ca2fecb5d17f8baacc431456
- https://argo-cd.readthedocs.io/en/stable/security_considerations/#cve-2020-8827-insufficient-anti-automationanti-brute-force
- https://github.com/argoproj/argo-cd

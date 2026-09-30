# [M] Bypassing Rate Limit and Brute Force Protection Using Cache Overflow

## Summary
Severity: Medium
Advisory: GHSA-2vgg-9h6w-m454
CVE: CVE-2024-21662
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-2vgg-9h6w-m454
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.8.13
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.9.0 <2.9.9
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.10.0 <2.10.4

## Details
### Summary
An attacker can effectively bypass the rate limit and brute force protections by exploiting the application's weak cache-based mechanism. This loophole in security can be combined with other vulnerabilities to attack the default admin account. This flaw undermines a previously [patched CVE](https://argo-cd.readthedocs.io/en/stable/security_considerations/#cve-2020-8827-insufficient-anti-automationanti-brute-force) intended to protect against brute-force attacks.

### Details
The application's brute force protection relies on a cache mechanism that tracks login attempts for each user. This cache is limited to a `defaultMaxCacheSize` of 1000 entries. An attacker can overflow this cache by bombarding it with login attempts for different users, thereby pushing out the admin account's failed attempts and effectively resetting the rate limit for that account.

The brute force protection mechanism's code:
```go
   if failed && len(failures) >= getMaximumCacheSize() {
       log.Warnf("Session cache size exceeds %d entries, removing random entry",

getMaximumCacheSize())
       idx := rand.Intn(len(failures) - 1)
       var rmUser string
       i := 0
       for key := range failures {

           if i == idx {
               rmUser = key

               delete(failures, key)

break

}

i++ }

       log.Infof("Deleted entry for user %s from cache", rmUser)
   }
```

### PoC
1. Set up the application environment and identify the login page.
2. Execute 4 failed login attempts for the admin account.
3. Run a Burp Intruder attack to populate the cache with login attempts for usernames ranging from 1 to 10000.
4. After 1000 attempts, start monitoring to see if the admin entries in the cache have been cleared.
5. At this point, brute-force the admin account.

In just 15 minutes, the PoC was able to perform 230 brute force attempts on the admin account. This rate allows for approximately 1000 requests per hour, effectively rendering the [older CVE](https://argo-cd.readthedocs.io/en/stable/security_considerations/#cve-2020-8827-insufficient-anti-automationanti-brute-force) rate limit patches useless.

### Impact
This is a severe vulnerability that enables attackers to perform brute force attacks at an accelerated rate, especially targeting the default admin account.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-2vgg-9h6w-m454
- https://nvd.nist.gov/vuln/detail/CVE-2024-21662
- https://github.com/argoproj/argo-cd/commit/17b0df1168a4c535f6f37e95f25ed7cd81e1fa4d
- https://github.com/argoproj/argo-cd/commit/6e181d72b31522f886a2afa029d5b26d7912ec7b
- https://github.com/argoproj/argo-cd/commit/cebb6538f7944c87ca2fecb5d17f8baacc431456
- https://argo-cd.readthedocs.io/en/stable/security_considerations/#cve-2020-8827-insufficient-anti-automationanti-brute-force
- https://github.com/argoproj/argo-cd

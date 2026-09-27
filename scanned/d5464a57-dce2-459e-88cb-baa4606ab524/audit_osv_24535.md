# [M] Sensitive information exposure in the logs of greader API in FreshRSS

## Summary
Severity: Medium
Advisory: CVE-2023-22481
Aliases: GHSA-8vvv-jxg6-8578
CVSS: 4.0 (CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2023-22481
Type: osv

## Details
FreshRSS is a self-hosted RSS feed aggregator. When using the greader API, the provided password is logged in clear in `users/_/log_api.txt` in the case where the authentication fails. The issues occurs in `authorizationToUser()` in `greader.php`. If there is an issue with the request or the credentials, `unauthorized()` or `badRequest()` is called. Both these functions are printing the return of `debugInfo()` in the logs.  `debugInfo()` will return the content of the request. By default, this will be saved in `users/_/log_api.txt` and if the const `COPY_LOG_TO_SYSLOG` is true, in syslogs as well. Exploiting this issue requires having access to logs produced by FreshRSS. Using the information from the logs, a malicious individual could get users' API keys (would be displayed if the users fills in a bad username) or passwords.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22481.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-8vvv-jxg6-8578
- https://nvd.nist.gov/vuln/detail/CVE-2023-22481
- https://github.com/FreshRSS/FreshRSS/commit/075cf4c800063e3cc65c3d41a9c23222e8ebb554

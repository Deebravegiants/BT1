# [H] Uses of deprecated API can be used to cause DoS in user-facing endpoints

## Summary
Severity: High
Advisory: GHSA-5q86-62xr-3r57
CVE: CVE-2022-31054
CWE: CWE-400, CWE-787
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-5q86-62xr-3r57
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-events` — affected >=0 <1.7.1

## Details
### Impact
Several `HandleRoute` endpoints make use of the deprecated `ioutil.ReadAll()`. `ioutil.ReadAll()` reads all the data into memory. As such, an attacker who sends a large request to the Argo Events server will be able to crash it and cause denial of service.

Eventsources susceptible to an out-of-memory denial-of-service attack:

- AWS SNS
- Bitbucket
- Bitbucket
- Gitlab
- Slack
- Storagegrid
- Webhook

### Patches
A patch for this vulnerability has been released in the following Argo Events version:

v1.7.1

### Credits
Disclosed by [Ada Logics](https://adalogics.com/) in a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
Open an issue in the [Argo Events issue tracker](https://github.com/argoproj/argo-events/issues) or [discussions](https://github.com/argoproj/argo-events/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-events

## References
- https://github.com/argoproj/argo-events/security/advisories/GHSA-5q86-62xr-3r57
- https://nvd.nist.gov/vuln/detail/CVE-2022-31054
- https://github.com/argoproj/argo-events/issues/1946
- https://github.com/argoproj/argo-events/pull/1966
- https://github.com/argoproj/argo-events/commit/eaabcb6d65022fc34a0cc9ea7f00681abd326b35
- https://github.com/argoproj/argo-events

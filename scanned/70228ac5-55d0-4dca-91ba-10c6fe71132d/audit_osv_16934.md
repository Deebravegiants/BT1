# [H] CVE-2020-10752

## Summary
Severity: High
Advisory: CVE-2020-10752
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-12
Source: https://osv.dev/vulnerability/CVE-2020-10752
Type: osv

## Details
A flaw was found in the OpenShift API Server, where it failed to sufficiently protect OAuthTokens by leaking them into the logs when an API Server panic occurred. This flaw allows an attacker with the ability to cause an API Server error to read the logs, and use the leaked OAuthToken to log into the API Server with the leaked token.

## References
- https://github.com/openshift/origin/blob/master/vendor/k8s.io/kubernetes/staging/src/k8s.io/apiserver/pkg/server/filters/wrap.go#L39
- https://github.com/openshift/enhancements/pull/323

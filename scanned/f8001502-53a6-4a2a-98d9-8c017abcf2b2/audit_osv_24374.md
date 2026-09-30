# [M] CVE-2023-1065

## Summary
Severity: Medium
Advisory: CVE-2023-1065
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-1065
Type: osv

## Details
This vulnerability in the Snyk Kubernetes Monitor can result in irrelevant data being posted to a Snyk Organization, which could in turn obfuscate other, relevant, security issues. It does not expose the user of the integration to any direct security risk and no user data can be leaked. To exploit the vulnerability the attacker does not need to be authenticated to Snyk but does need to know the target's Integration ID (which may or may not be the same as the Organization ID, although this is an unpredictable UUID in either case).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1065.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1065
- https://github.com/snyk/kubernetes-monitor/commit/5b9a7821680bbfb6c4a900ab05d898ce2b2cc157
- https://github.com/snyk/kubernetes-monitor/pull/1275
- https://github.com/snyk/kubernetes-monitor
- https://snyk.io/blog/api-auth-vuln-snyk-kubernetes-cve-2023-1065/

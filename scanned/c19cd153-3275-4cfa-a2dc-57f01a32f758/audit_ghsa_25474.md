# [C] Helm Unsafe Link Following

## Summary
Severity: Critical
Advisory: GHSA-p5pc-m4q7-7qm9
CVE: CVE-2019-18658
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p5pc-m4q7-7qm9
Type: github-advisory

## Affected
- Go: `helm.sh/helm` — affected >=2.0.0 <2.15.2

## Details
In Helm 2.x before 2.15.2, commands that deal with loading a chart as a directory or packaging a chart provide an opportunity for a maliciously designed chart to include sensitive content such as `/etc/passwd`, or to execute a denial of service (DoS) via a special file such as /dev/urandom, via symlinks. No version of Tiller is known to be impacted. This is a client-only issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18658
- https://github.com/helm/helm
- https://helm.sh/blog/2019-10-30-helm-symlink-security-notice

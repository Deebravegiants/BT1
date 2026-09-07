# [M] CRI-O vulnerable to /etc/passwd tampering resulting in Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-cm9x-c3rh-7rc4
CVE: CVE-2022-4318
CWE: CWE-538, CWE-913
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2022-12-29
Source: https://github.com/advisories/GHSA-cm9x-c3rh-7rc4
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.26.0

## Details
### Impact
It is possible to craft an environment variable with newlines to add entries to a container's /etc/passwd. It is possible to circumvent admission validation of username/UID by adding such an entry.

Note: because the pod author is in control of the container's /etc/passwd, this is not considered a new risk factor. However, this advisory is being opened for transparency and as a way of tracking fixes.

### Patches
1.26.0 will have the fix. More patches will be posted as they're available.

### Workarounds
Additional security controls like SELinux should prevent any damage a container is able to do with root on the host. Using SELinux is recommended because this class of attack is already possible by manually editing the container's /etc/passwd 

### References

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-cm9x-c3rh-7rc4
- https://nvd.nist.gov/vuln/detail/CVE-2022-4318
- https://github.com/cri-o/cri-o/pull/6450
- https://access.redhat.com/errata/RHSA-2023:1033
- https://access.redhat.com/errata/RHSA-2023:1503
- https://access.redhat.com/security/cve/CVE-2022-4318
- https://bugzilla.redhat.com/show_bug.cgi?id=2152703
- https://github.com/cri-o/cri-o

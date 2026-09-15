# [M] CloudCore CSI Driver: Malicious response from KubeEdge can crash CSI Driver controller server

## Summary
Severity: Medium
Advisory: GHSA-x938-fvfw-7jh5
CVE: CVE-2022-31077
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-25
Source: https://github.com/advisories/GHSA-x938-fvfw-7jh5
Type: github-advisory

## Affected
- Go: `github.com/kubeedge/kubeedge` — affected >=1.10.0 <1.10.1
- Go: `github.com/kubeedge/kubeedge` — affected >=0 <1.9.3

## Details
### Impact
A malicious message response from KubeEdge can crash the CSI Driver controller server by triggering a nil-pointer dereference panic. As a consequence, the CSI Driver controller will be in denial of service. An attacker would already need to be an authenticated user of the Cloud, and only when the authenticated user launches the `csidriver` then CloudCore may be attacked.

### Patches
This bug has been fixed in Kubeedge 1.11.0, 1.10.1, and 1.9.3. Users should update to these versions to resolve the issue.

### Workarounds
At the time of writing, no workaround exists.

### References
NA

### Credits
Thanks David Korczynski and Adam Korczynski of ADA Logics for responsibly disclosing this issue in accordance with the [kubeedge security policy](https://github.com/kubeedge/kubeedge/security/policy) during a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [KubeEdge repo](https://github.com/kubeedge/kubeedge/issues/new/choose)
* To make a vulnerability report, email your vulnerability to the private [cncf-kubeedge-security@lists.cncf.io](mailto:cncf-kubeedge-security@lists.cncf.io) list with the security details and the details expected for [KubeEdge bug reports](https://github.com/kubeedge/kubeedge/blob/master/.github/ISSUE_TEMPLATE/bug-report.md).

**Notes:** This vulnerability was found by fuzzing KubeEdge by way of OSS-Fuzz.

## References
- https://github.com/kubeedge/kubeedge/security/advisories/GHSA-x938-fvfw-7jh5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31077
- https://github.com/kubeedge/kubeedge/pull/3899
- https://github.com/kubeedge/kubeedge/pull/3899/commits/5d60ae9eabd6b6b7afe38758e19bbe8137664701
- https://github.com/kubeedge/kubeedge

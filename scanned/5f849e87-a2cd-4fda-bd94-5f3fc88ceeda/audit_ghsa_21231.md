# [M] KubeEdge Cloud AdmissionController component DoS

## Summary
Severity: Medium
Advisory: GHSA-w52j-3457-q9wr
CVE: CVE-2022-31074
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-11
Source: https://github.com/advisories/GHSA-w52j-3457-q9wr
Type: github-advisory

## Affected
- Go: `github.com/kubeedge/kubeedge` — affected >=1.11.0 <1.11.1
- Go: `github.com/kubeedge/kubeedge` — affected >=1.10.0 <1.10.2
- Go: `github.com/kubeedge/kubeedge` — affected >=0 <1.9.4

## Details
### Impact
Several endpoints including `/devicemodels`, `/rules`, `/ruleendpoints`, `/offlinemigration` in the Cloud Admissioncontroller may be susceptible to a DoS attack if an HTTP request containing a very large Body is sent to it.
Only an authenticated user can cause this issue. It will be affected when users deploy a Cloud Admissioncontroller. The consequence of the exhaustion is that the Cloud Admissioncontroller will be in denial of service.

### Patches
This bug has been fixed in Kubeedge 1.11.1, 1.10.2, 1.9.4. Users should update to these versions to resolve the issue.

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

## References
- https://github.com/kubeedge/kubeedge/security/advisories/GHSA-w52j-3457-q9wr
- https://nvd.nist.gov/vuln/detail/CVE-2022-31074
- github.com/kubeedge/kubeedge

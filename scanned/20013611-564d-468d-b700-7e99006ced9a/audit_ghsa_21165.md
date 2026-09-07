# [M] KubeEdge Cloud Stream and Edge Stream DoS from large stream message

## Summary
Severity: Medium
Advisory: GHSA-wrcr-x4qj-j543
CVE: CVE-2022-31079
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-11
Source: https://github.com/advisories/GHSA-wrcr-x4qj-j543
Type: github-advisory

## Affected
- Go: `github.com/kubeedge/kubeedge` — affected >=1.11.0 <1.11.1
- Go: `github.com/kubeedge/kubeedge` — affected >=1.10.0 <1.10.2
- Go: `github.com/kubeedge/kubeedge` — affected >=0 <1.9.4

## Details
### Impact
The Cloud Stream server and the Edge Stream server reads the entire message into memory without imposing a limit on the size of this message. An attacker can exploit this by sending a large message to exhaust memory and cause a DoS. The Cloud Stream server and the Edge Stream server are under DoS attack in this case. The consequence of the exhaustion is that the CloudCore and EdgeCore will be in a denial of service.
Only an authenticated user can cause this issue. It will be affected only when users enable cloudStream module in the config file cloudcore.yaml and enable edgeStream module in the config file edgecore.yaml as below.
cloudcore.yaml:
```
modules:
  ...
  cloudStream:
    enable: true
```
edgecore.yaml:
```
modules:
  ...
  edgeStream:
    enable: true
```

### Patches
This bug has been fixed in Kubeedge 1.11.1, 1.10.2, 1.9.4. Users should update to these versions to resolve the issue.

### Workarounds
Disable cloudStream module in the config file cloudcore.yaml and disable edgeStream module in the config file edgecore.yaml, restart process cloudcore and edgecore after modification.

### References
NA

### Credits
Thanks David Korczynski and Adam Korczynski of ADA Logics for responsibly disclosing this issue in accordance with the [kubeedge security policy](https://github.com/kubeedge/kubeedge/security/policy) during a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [KubeEdge repo](https://github.com/kubeedge/kubeedge/issues/new/choose)
* To make a vulnerability report, email your vulnerability to the private [cncf-kubeedge-security@lists.cncf.io](mailto:cncf-kubeedge-security@lists.cncf.io) list with the security details and the details expected for [KubeEdge bug reports](https://github.com/kubeedge/kubeedge/blob/master/.github/ISSUE_TEMPLATE/bug-report.md).

## References
- https://github.com/kubeedge/kubeedge/security/advisories/GHSA-wrcr-x4qj-j543
- https://nvd.nist.gov/vuln/detail/CVE-2022-31079
- https://github.com/kubeedge/kubeedge

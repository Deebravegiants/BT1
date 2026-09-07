# [M] KubeEdge CloudCore Router memory exhaustion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qpx3-9565-5xwm
CVE: CVE-2022-31078
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-11
Source: https://github.com/advisories/GHSA-qpx3-9565-5xwm
Type: github-advisory

## Affected
- Go: `github.com/kubeedge/kubeedge` — affected >=1.11.0 <1.11.1
- Go: `github.com/kubeedge/kubeedge` — affected >=1.10.0 <1.10.2
- Go: `github.com/kubeedge/kubeedge` — affected >=0 <1.9.4

## Details
### Impact
The CloudCore Router does not impose a limit on the size of responses to requests made by the REST handler. An attacker could use this weakness to make a request that will return an HTTP response with a large body and cause DoS of CloudCore. In the HTTP Handler API, the rest handler makes a request to a pre-specified handle. The handle will return an HTTP response that is then read into memory. The consequence of the exhaustion is that CloudCore will be in a denial of service.
Only an authenticated user of the cloud can make an attack. It will be affected only when users enable `router` module in the config file `cloudcore.yaml` as below.
```
modules:
  ...
  router:
    enable: true
```

### Patches
This bug has been fixed in Kubeedge 1.11.1, 1.10.2, 1.9.4. Users should update to these versions to resolve the issue.

### Workarounds
Disable the router module in the config file `cloudcore.yaml`.

### References
NA

### Credits
Thanks David Korczynski and Adam Korczynski of ADA Logics for responsibly disclosing this issue in accordance with the [kubeedge security policy](https://github.com/kubeedge/kubeedge/security/policy) during a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [KubeEdge repo](https://github.com/kubeedge/kubeedge/issues/new/choose)
* To make a vulnerability report, email your vulnerability to the private [cncf-kubeedge-security@lists.cncf.io](mailto:cncf-kubeedge-security@lists.cncf.io) list with the security details and the details expected for [KubeEdge bug reports](https://github.com/kubeedge/kubeedge/blob/master/.github/ISSUE_TEMPLATE/bug-report.md).

## References
- https://github.com/kubeedge/kubeedge/security/advisories/GHSA-qpx3-9565-5xwm
- https://nvd.nist.gov/vuln/detail/CVE-2022-31078
- https://github.com/kubeedge/kubeedge

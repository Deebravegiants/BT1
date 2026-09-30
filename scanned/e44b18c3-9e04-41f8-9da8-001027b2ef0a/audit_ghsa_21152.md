# [M] KubeEdge Edge ServiceBus module DoS

## Summary
Severity: Medium
Advisory: GHSA-vwm6-qc77-v2rh
CVE: CVE-2022-31073
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-11
Source: https://github.com/advisories/GHSA-vwm6-qc77-v2rh
Type: github-advisory

## Affected
- Go: `github.com/kubeedge/kubeedge` — affected >=1.11.0 <1.11.1
- Go: `github.com/kubeedge/kubeedge` — affected >=1.10.0 <1.10.2
- Go: `github.com/kubeedge/kubeedge` — affected >=0 <1.9.4

## Details
### Impact
The ServiceBus server on the edge side may be susceptible to a DoS attack if an HTTP request containing a very large Body is sent to it.
It is possible for the node to be exhausted of memory. The consequence of the exhaustion is that other services on the node, e.g. other containers, will be unable to allocate memory and thus causing a denial of service.
Malicious Apps which by accident pulled by users on the host and have the access to send HTTP requests to localhost may make an attack. It will be affected only when users enable the `ServiceBus` module in the config file `edgecore.yaml` as below:
```
modules:
  ...
  serviceBus:
    enable: true
```

### Patches
This bug has been fixed in Kubeedge 1.11.1, 1.10.2, 1.9.4. Users should update to these versions to resolve the issue.

### Workarounds
Disable the ServiceBus module in the config file `edgecore.yaml`.

### References
NA

### Credits
Thanks David Korczynski and Adam Korczynski of ADA Logics for responsibly disclosing this issue in accordance with the [kubeedge security policy](https://github.com/kubeedge/kubeedge/security/policy) during a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [KubeEdge repo](https://github.com/kubeedge/kubeedge/issues/new/choose)
* To make a vulnerability report, email your vulnerability to the private [cncf-kubeedge-security@lists.cncf.io](mailto:cncf-kubeedge-security@lists.cncf.io) list with the security details and the details expected for [KubeEdge bug reports](https://github.com/kubeedge/kubeedge/blob/master/.github/ISSUE_TEMPLATE/bug-report.md).

## References
- https://github.com/kubeedge/kubeedge/security/advisories/GHSA-vwm6-qc77-v2rh
- https://nvd.nist.gov/vuln/detail/CVE-2022-31073
- https://github.com/kubeedge/kubeedge/pull/4038
- https://github.com/kubeedge/kubeedge/pull/4039
- https://github.com/kubeedge/kubeedge/pull/4042
- github.com/kubeedge/kubeedge

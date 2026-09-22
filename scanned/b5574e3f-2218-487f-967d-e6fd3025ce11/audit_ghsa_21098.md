# [M] KubeEdge DoS when signing the CSR from EdgeCore

## Summary
Severity: Medium
Advisory: GHSA-x3px-2p95-f6jr
CVE: CVE-2022-31075
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-11
Source: https://github.com/advisories/GHSA-x3px-2p95-f6jr
Type: github-advisory

## Affected
- Go: `github.com/kubeedge/kubeedge` — affected >=1.11.0 <1.11.1
- Go: `github.com/kubeedge/kubeedge` — affected >=1.10.0 <1.10.2
- Go: `github.com/kubeedge/kubeedge` — affected >=0 <1.9.4

## Details
### Impact
EdgeCore may be susceptible to a DoS attack on CloudHub if an attacker was to send a well-crafted HTTP request to `/edge.crt`.
If an attacker can send a well-crafted HTTP request to CloudHub, and that request has a very large body, that request could crash the HTTP service through a memory exhaustion vector. The request body is being read into memory, and a body that was larger than the available memory could lead to a successful attack.
Because the request would have to make it through authorization, only authorized users could perform this attack. The consequence of the exhaustion is that CloudHub will be in denial of service. It will be affected only when users enable the CloudHub module in the file `cloudcore.yaml` as below:
```
modules:
  ...
  cloudHub:
    enable: true
```

### Patches
This bug has been fixed in Kubeedge 1.11.1, 1.10.2, 1.9.4. Users should update to these versions to resolve the issue.

### Workarounds
Disable the CloudHub module in the config file `cloudcore.yaml`.

### References
NA

### Credits
Thanks David Korczynski and Adam Korczynski of ADA Logics for responsibly disclosing this issue in accordance with the [kubeedge security policy](https://github.com/kubeedge/kubeedge/security/policy) during a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [KubeEdge repo](https://github.com/kubeedge/kubeedge/issues/new/choose)
* To make a vulnerability report, email your vulnerability to the private [cncf-kubeedge-security@lists.cncf.io](mailto:cncf-kubeedge-security@lists.cncf.io) list with the security details and the details expected for [KubeEdge bug reports](https://github.com/kubeedge/kubeedge/blob/master/.github/ISSUE_TEMPLATE/bug-report.md).

## References
- https://github.com/kubeedge/kubeedge/security/advisories/GHSA-x3px-2p95-f6jr
- https://nvd.nist.gov/vuln/detail/CVE-2022-31075
- github.com/kubeedge/kubeedge

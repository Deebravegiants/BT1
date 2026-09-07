# [H] Talos vulnerable dependency due to race condition in Linux kernel's IP framework XFRM

## Summary
Severity: High
Advisory: GHSA-34vw-m4rh-r36p
CWE: CWE-362, CWE-787
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-34vw-m4rh-r36p
Type: github-advisory

## Affected
- Go: `github.com/talos-systems/talos` — affected >=0 <1.2.0

## Details
### Impact
A race condition was found in the Linux kernel's IP framework for transforming packets (XFRM subsystem) when multiple calls to xfrm_probe_algs occurred simultaneously. This flaw could allow a local attacker to potentially trigger an out-of-bounds write or leak kernel heap memory by performing an out-of-bounds read and copying it into a socket.

### Patches
The fix has been backported to [5.15.64](https://www.linuxkernelcves.com/cves/CVE-2022-3028) version of the upstream Linux kernel (5.15 is the upstream Kernel long term version Talos ships with). Talos >= v1.2.0 is shipped with Linux Kernel 5.15.64 fixing the above issue.

Kubernetes workloads running in Talos are not affected since user namespaces are disabled in Talos kernel config. So an unprivileged user cannot obtain CAP_NET_ADMIN by unsharing. However untrusted workloads that run with privileged: true or having NET_ADMIN capability poses a risk.

### Workarounds
Audit kubernetes workloads running in the cluster with privileged: true set or having NET_ADMIN capability and assess the threat vector.

### References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3028
- https://access.redhat.com/security/cve/CVE-2022-3028

### For more information
- Email us at [security@siderolabs.com](mailto:security@siderolabs.com)

## References
- https://github.com/siderolabs/talos/security/advisories/GHSA-34vw-m4rh-r36p
- https://github.com/siderolabs/talos

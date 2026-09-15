# [H] Talos Linux has a local privilege escalation from untrusted workloads

## Summary
Severity: High
Advisory: GHSA-m38g-vww2-mvgx
CWE: CWE-669
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-m38g-vww2-mvgx
Type: github-advisory

## Affected
- Go: `github.com/siderolabs/talos` — affected >=0 <1.12.7

## Details
### Summary

A vulnerability in the Linux kernel's algif_aead subsystem (CVE-2026-31431, "copy.fail") allows an unprivileged container workload to corrupt arbitrary file page-cache pages via the AF_ALG crypto interface and splice(). On Talos Linux, this vulnerability can be chained into a complete node compromise: an attacker who can schedule a pod on a worker node can, without any elevated Kubernetes permissions, achieve arbitrary code execution as root on the host (by poisoning a binary inside a privileged pod, or poisoning a binary which runs with elevated privileges like a CNI binary), access host filesystem, including node secrets. 

The exploit does not require kernel debugging, race conditions, or any prior privileges beyond the ability to create a pod.

### Impact

An attacker with the ability to deploy a Kubernetes pod on an affected node can:

1. Corrupt the page-cache of /usr/sbin/nft in the containerd snapshot layer shared between the attacker's pod and the kube-proxy DaemonSet. Because containerd reuses XFS page-cache pages across overlayfs mounts sharing the same lower layer, the corruption is immediately visible to all containers using that image layer — including privileged system DaemonSets.
2. Execute arbitrary code inside kube-proxy — a privileged DaemonSet running on every node with all Linux capabilities (privileged: true) and host network access — the next time kube-proxy invokes nft as part of its nftables reconciliation loop (typically within seconds).
3. At this point, an attacker achieved code execution inside a privileged pod, which allows to escape to the host.
4. Same attack can be planted by infiltrating other binaries running as privileged, for example a CNI plugin.

### Patches

Upgrade to Talos v1.13.0 or Talos v1.12.7 which ships Linux kernel 6.18.25. The kernel fix for CVE-2026-31431 (algif_aead in-place optimization revert) was committed upstream in  Linux 6.18.22 and is included in all Talos releases from v1.13.0 and Talos 1.12.7 onwards.

### Workarounds

There are multiple workarounds available based on the situation, but we really recommend to upgrade.

#### Option 1 - Change kernel arguments

Add a kernel argument with `initcall_blacklist=algif_aead_init` by upgrading Talos to the same version.

> Note: this either requires setting `machine.kernel.extraKernelArgs` if using BIOS based boot or upgrading with a new image from factory/imager generated image by setting the extra kernel args. See [Boot Assets](https://docs.siderolabs.com/talos/v1.13/platform-specific-installations/boot-assets)

#### Option 2 - Deploy all workload pods with a seccomp profile denying  creating `AF_ALG` socket creation

`patch.yaml`

```yaml
machine:
  seccompProfiles:
    - name: copy-fail-block.json
      value:
        defaultAction: SCMP_ACT_ALLOW
        syscalls:
          - names:
              - socket
            action: SCMP_ACT_ERRNO
            args:
              - index: 0
                value: 38
                op: SCMP_CMP_EQ
```

Apply this patch to all machines in the cluster and set this for all the pod spec:

```yaml
...
spec:
      securityContext:
        seccompProfile:
          type: Localhost
          localhostProfile: profiles/copy-fail-block.json
```

#### Option 3 - Block the syscall in runtime with a eBPF program

See [copy-fail-blocker](https://github.com/cozystack/copy-fail-blocker), this can be applied to a running system without a reboot, but it has to run before any other workloads are scheduled after a reboot. 

### References

* https://copy.fail/
* https://xint.io/blog/copy-fail-linux-distributions
* https://github.com/theori-io/copy-fail-CVE-2026-31431
* https://github.com/Percivalll/Copy-Fail-CVE-2026-31431-Kubernetes-PoC

## References
- https://github.com/siderolabs/talos/security/advisories/GHSA-m38g-vww2-mvgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-31431
- https://github.com/Percivalll/Copy-Fail-CVE-2026-31431-Kubernetes-PoC
- https://github.com/siderolabs/talos
- https://github.com/theori-io/copy-fail-CVE-2026-31431
- https://xint.io/blog/copy-fail-linux-distributions

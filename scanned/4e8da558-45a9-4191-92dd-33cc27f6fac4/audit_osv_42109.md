# [C] nvmet-tcp: Fix potential UAF when ddgst mismatch

## Summary
Severity: Critical
Advisory: CVE-2026-64535
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64535
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.12.0 <6.1.178, >=5.16.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: Fix potential UAF when ddgst mismatch

Shivam Kumar found via vulnerability testing:
When data digest is enabled on an NVMe/TCP connection and a digest
mismatch occurs on a non-final H2C_DATA PDU during an R2T-based
data transfer, the digest error handler in nvmet_tcp_try_recv_ddgst()
calls nvmet_req_uninit() — which performs percpu_ref_put() on the
submission queue — but does NOT mark the command as completed. It
does not set cqe->status, does not modify rbytes_done, and does not
clear any flag. When the subsequent fatal error triggers queue
teardown, nvmet_tcp_uninit_data_in_cmds() iterates all commands,
checks nvmet_tcp_need_data_in() for each one, and finds that the
already-uninited command still appears to need data (because
rbytes_done < transfer_len and cqe->status == 0). It therefore calls
nvmet_req_uninit() a second time on the same command — a double
percpu_ref_put against a single percpu_ref_get.

## References
- https://git.kernel.org/stable/c/088ee46c18d99baef453afd74181dd40ade044ad
- https://git.kernel.org/stable/c/6f9442983a3e4227afd1c83a5251ddbca585ea21
- https://git.kernel.org/stable/c/7e558308eba14c8136cb1e615f0c850f76d1fc0a
- https://git.kernel.org/stable/c/96fe2513df590e74b04253a45089cae75569570e
- https://git.kernel.org/stable/c/dbbd07d0a7020b80f6a7028e561908f7b83b3d5a
- https://git.kernel.org/stable/c/dfb902462bca478f050224ec7a7195aafa7643b1
- https://git.kernel.org/stable/c/e091ff83d962f9ed00d9bd70443676de9fe98bdc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64535.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64535
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

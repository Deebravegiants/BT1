# [C] nvmet-tcp: check INIT_FAILED before nvmet_req_uninit in digest error path

## Summary
Severity: Critical
Advisory: CVE-2026-64534
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64534
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.12.0 <6.1.178, >=5.16.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: check INIT_FAILED before nvmet_req_uninit in digest error path

In nvmet_tcp_try_recv_ddgst(), when a data digest mismatch is detected,
nvmet_req_uninit() is called unconditionally. However, if the command
arrived via the nvmet_tcp_handle_req_failure() path, nvmet_req_init()
had returned false and percpu_ref_tryget_live() was never executed. The
unconditional percpu_ref_put() inside nvmet_req_uninit() then causes a
refcount underflow, leading to a WARNING in
percpu_ref_switch_to_atomic_rcu, a use-after-free diagnostic, and
eventually a permanent workqueue deadlock.

Check cmd->flags & NVMET_TCP_F_INIT_FAILED before calling
nvmet_req_uninit(), matching the existing pattern in
nvmet_tcp_execute_request().

## References
- https://git.kernel.org/stable/c/22ec7a9fe9153d2737ee9b2fa6d2e43a1491decf
- https://git.kernel.org/stable/c/2ed3c9d955e8cd6361f130623baa664a75fb345f
- https://git.kernel.org/stable/c/4606467a75cfc16721937272ed29462a750b60c8
- https://git.kernel.org/stable/c/ba35b1c674ca3841c0dfadd698f2c1b3ec542d4e
- https://git.kernel.org/stable/c/c7874dad84b20433c0fe3919f291a762d40de08b
- https://git.kernel.org/stable/c/d306da8833e75f669d93424fd84940236f3850bc
- https://git.kernel.org/stable/c/e602c93b25bda4a9d0ff1791a4bdbfdcbb074af1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64534.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64534
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

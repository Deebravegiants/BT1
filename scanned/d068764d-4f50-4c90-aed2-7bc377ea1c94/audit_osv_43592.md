# [C] rxrpc: serialize kernel accept preallocation with socket teardown

## Summary
Severity: Critical
Advisory: CVE-2026-74436
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74436
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: serialize kernel accept preallocation with socket teardown

rxrpc_kernel_charge_accept() reads rx->backlog without any
socket/backlog synchronization and passes that raw pointer into
rxrpc_service_prealloc_one(). A concurrent rxrpc_discard_prealloc()
sets rx->backlog = NULL and frees the backlog rings, so a kernel
preallocation worker can keep using a freed struct rxrpc_backlog
while updating *_backlog_head/tail and array slots.

Serialize the state check and backlog lookup with the socket lock,
and reject kernel preallocation once teardown has disabled
listening or discarded the service backlog.

## References
- https://git.kernel.org/stable/c/0337cdba0c477f176c0459bed012109453184573
- https://git.kernel.org/stable/c/11b429b84c87cb5a0152f14e7d6cb649ed363901
- https://git.kernel.org/stable/c/1741378a7a83dfd8e53a9196730df709b903cd33
- https://git.kernel.org/stable/c/35a967ff8b24db09ee429c39c5b5e6571639997d
- https://git.kernel.org/stable/c/c20d983968f239574290cf804a58cde18ad1c559
- https://git.kernel.org/stable/c/d6207326b4ca0ae1041281b6af9df53f8080669a
- https://git.kernel.org/stable/c/dc175389b18c29a5303ee83169ec653adfae3e17
- https://git.kernel.org/stable/c/dfa0b2bbc5e50119f89c6b5407faa5ed86dfa7c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74436.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74436
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] can: bcm: extend bcm_tx_lock usage for data and timer updates

## Summary
Severity: High
Advisory: CVE-2026-72119
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72119
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: extend bcm_tx_lock usage for data and timer updates

Stage new CAN frame content for an existing tx op into a kmalloc()'d
buffer and validate it there, mirroring the approach already used in
bcm_rx_setup(). Only copy the validated data into op->frames while
holding op->bcm_tx_lock, so bcm_can_tx() and bcm_tx_timeout_handler()
can no longer observe a partially updated or unvalidated frame.

Add a missing error path for memcpy_from_msg() when copying CAN frame
data from userspace.

Also move the kt_ival1/kt_ival2/ival1/ival2 updates in bcm_tx_setup()
under op->bcm_tx_lock, and read kt_ival1/kt_ival2/count under the same
lock in bcm_tx_set_expiry() and bcm_tx_timeout_handler(), closing the
torn 64-bit ktime_t read on 32-bit platforms.

## References
- https://git.kernel.org/stable/c/12ce799f7ab1e05bd8fbf79e46f403bfe5597ebc
- https://git.kernel.org/stable/c/337f966c00662d81ad82cf5a4bbb150b2e32c0d4
- https://git.kernel.org/stable/c/37917e432e50b7de2b64230974380132a30f7270
- https://git.kernel.org/stable/c/52f06e7603780de100233713ddaf971d422e10ef
- https://git.kernel.org/stable/c/63422347b4c782f429748b2a09cd3cf3b77e6abd
- https://git.kernel.org/stable/c/972fd66bb08fdef1090abe43196ca8da07216d13
- https://git.kernel.org/stable/c/a538b072ee074c9b41b9d9c15a6861a963e30755
- https://git.kernel.org/stable/c/bd46f55dec608daa44b45dcf3328517630ad8e40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72119.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72119
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [C] tls: Fix race condition in tls_sw_cancel_work_tx()

## Summary
Severity: Critical
Advisory: CVE-2026-23240
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-23240
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: Fix race condition in tls_sw_cancel_work_tx()

This issue was discovered during a code audit.

After cancel_delayed_work_sync() is called from tls_sk_proto_close(),
tx_work_handler() can still be scheduled from paths such as the
Delayed ACK handler or ksoftirqd.
As a result, the tx_work_handler() worker may dereference a freed
TLS object.

The following is a simple race scenario:

          cpu0                         cpu1

tls_sk_proto_close()
  tls_sw_cancel_work_tx()
                                 tls_write_space()
                                   tls_sw_write_space()
                                     if (!test_and_set_bit(BIT_TX_SCHEDULED, &tx_ctx->tx_bitmask))
    set_bit(BIT_TX_SCHEDULED, &ctx->tx_bitmask);
    cancel_delayed_work_sync(&ctx->tx_work.work);
                                     schedule_delayed_work(&tx_ctx->tx_work.work, 0);

To prevent this race condition, cancel_delayed_work_sync() is
replaced with disable_delayed_work_sync().

## References
- https://git.kernel.org/stable/c/17153f154f80be2b47ebf52840f2d8f724eb2f3b
- https://git.kernel.org/stable/c/7bb09315f93dce6acc54bf59e5a95ba7365c2be4
- https://git.kernel.org/stable/c/854cd32bc74fe573353095e90958490e4e4d641b
- https://git.kernel.org/stable/c/a5de36d6cee74a92c1a21b260bc507e64bc451de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23240.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

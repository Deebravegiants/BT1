# [H] net/smc: fix NULL sndbuf_desc in smc_cdc_tx_handler()

## Summary
Severity: High
Advisory: CVE-2023-53110
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53110
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.176, >=5.11.0 <5.15.104, >=5.16.0 <6.1.21, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix NULL sndbuf_desc in smc_cdc_tx_handler()

When performing a stress test on SMC-R by rmmod mlx5_ib driver
during the wrk/nginx test, we found that there is a probability
of triggering a panic while terminating all link groups.

This issue dues to the race between smc_smcr_terminate_all()
and smc_buf_create().

			smc_smcr_terminate_all

smc_buf_create
/* init */
conn->sndbuf_desc = NULL;
...

			__smc_lgr_terminate
				smc_conn_kill
					smc_close_abort
						smc_cdc_get_slot_and_msg_send

			__softirqentry_text_start
				smc_wr_tx_process_cqe
					smc_cdc_tx_handler
						READ(conn->sndbuf_desc->len);
						/* panic dues to NULL sndbuf_desc */

conn->sndbuf_desc = xxx;

This patch tries to fix the issue by always to check the sndbuf_desc
before send any cdc msg, to make sure that no null pointer is
seen during cqe processing.

## References
- https://git.kernel.org/stable/c/22a825c541d775c1dbe7b2402786025acad6727b
- https://git.kernel.org/stable/c/31817c530768b0199771ec6019571b4f0ddbf230
- https://git.kernel.org/stable/c/3c270435db8aa34929263dddae8fd050f5216ecb
- https://git.kernel.org/stable/c/3ebac7cf0a184a8102821a7a00203f02bebda83c
- https://git.kernel.org/stable/c/b108bd9e6be000492ebebe867daa699285978a10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53110.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

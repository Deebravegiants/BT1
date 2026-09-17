# [H] padata: avoid UAF for reorder_work

## Summary
Severity: High
Advisory: CVE-2025-21726
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21726
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

padata: avoid UAF for reorder_work

Although the previous patch can avoid ps and ps UAF for _do_serial, it
can not avoid potential UAF issue for reorder_work. This issue can
happen just as below:

crypto_request			crypto_request		crypto_del_alg
padata_do_serial
  ...
  padata_reorder
    // processes all remaining
    // requests then breaks
    while (1) {
      if (!padata)
        break;
      ...
    }

				padata_do_serial
				  // new request added
				  list_add
    // sees the new request
    queue_work(reorder_work)
				  padata_reorder
				    queue_work_on(squeue->work)
...

				<kworker context>
				padata_serial_worker
				// completes new request,
				// no more outstanding
				// requests

							crypto_del_alg
							  // free pd

<kworker context>
invoke_padata_reorder
  // UAF of pd

To avoid UAF for 'reorder_work', get 'pd' ref before put 'reorder_work'
into the 'serial_wq' and put 'pd' ref until the 'serial_wq' finish.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/4c6209efea2208597dbd3e52dc87a0d1a8f2dbe1
- https://git.kernel.org/stable/c/6f45ef616775b0ce7889b0f6077fc8d681ab30bc
- https://git.kernel.org/stable/c/7000507bb0d2ceb545c0a690e0c707c897d102c2
- https://git.kernel.org/stable/c/8ca38d0ca8c3d30dd18d311f1a7ec5cb56972cac
- https://git.kernel.org/stable/c/a54091c24220a4cd847d5b4f36d678edacddbaf0
- https://git.kernel.org/stable/c/dd7d37ccf6b11f3d95e797ebe4e9e886d0332600
- https://git.kernel.org/stable/c/f4f1b1169fc3694f9bc3e28c6c68dbbf4cc744c0
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21726.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21726
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

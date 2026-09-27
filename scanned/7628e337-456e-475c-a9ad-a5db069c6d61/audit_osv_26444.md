# [H] media: netup_unidvb: fix use-after-free at del_timer()

## Summary
Severity: High
Advisory: CVE-2023-53219
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53219
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: netup_unidvb: fix use-after-free at del_timer()

When Universal DVB card is detaching, netup_unidvb_dma_fini()
uses del_timer() to stop dma->timeout timer. But when timer
handler netup_unidvb_dma_timeout() is running, del_timer()
could not stop it. As a result, the use-after-free bug could
happen. The process is shown below:

    (cleanup routine)          |        (timer routine)
                               | mod_timer(&dev->tx_sim_timer, ..)
netup_unidvb_finidev()         | (wait a time)
  netup_unidvb_dma_fini()      | netup_unidvb_dma_timeout()
    del_timer(&dma->timeout);  |
                               |   ndev->pci_dev->dev //USE

Fix by changing del_timer() to del_timer_sync().

## References
- https://git.kernel.org/stable/c/051af3f0b7d1cd8ab7f3e2523ad8ae1af44caba3
- https://git.kernel.org/stable/c/07821524f67bf920342bc84ae8b3dea2a315a89e
- https://git.kernel.org/stable/c/0f5bb36bf9b39a2a96e730bf4455095b50713f63
- https://git.kernel.org/stable/c/1550bcf2983ae1220cc8ab899a39a423fa7cb523
- https://git.kernel.org/stable/c/90229e9ee957d4514425e4a4d82c50ab5d57ac4d
- https://git.kernel.org/stable/c/c8f9c05e1ebcc9c7bc211cc8b74d8fb86a8756fc
- https://git.kernel.org/stable/c/dd5c77814f290b353917df329f36de1472d47154
- https://git.kernel.org/stable/c/f9982db735a8495eee14267cf193c806b957e942
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53219.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53219
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

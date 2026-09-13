# [H] media: bttv: fix use after free error due to btv->timeout timer

## Summary
Severity: High
Advisory: CVE-2023-52847
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52847
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.299, >=4.20.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: bttv: fix use after free error due to btv->timeout timer

There may be some a race condition between timer function
bttv_irq_timeout and bttv_remove. The timer is setup in
probe and there is no timer_delete operation in remove
function. When it hit kfree btv, the function might still be
invoked, which will cause use after free bug.

This bug is found by static analysis, it may be false positive.

Fix it by adding del_timer_sync invoking to the remove function.

cpu0                cpu1
                  bttv_probe
                    ->timer_setup
                      ->bttv_set_dma
                        ->mod_timer;
bttv_remove
  ->kfree(btv);
                  ->bttv_irq_timeout
                    ->USE btv

## References
- https://git.kernel.org/stable/c/1871014d6ef4812ad11ef7d838d73ce09d632267
- https://git.kernel.org/stable/c/20568d06f6069cb835e05eed432edf962645d226
- https://git.kernel.org/stable/c/2f3d9198cdae1cb079ec8652f4defacd481eab2b
- https://git.kernel.org/stable/c/51c94256a83fe4e17406c66ff3e1ad7d242d8574
- https://git.kernel.org/stable/c/847599fffa528b2cdec4e21b6bf7586dad982132
- https://git.kernel.org/stable/c/b35fdade92c5058a5e727e233fe263b828de2c9a
- https://git.kernel.org/stable/c/bbc3b8dd2cb7817e703f112d988e4f4728f0f2a9
- https://git.kernel.org/stable/c/bd5b50b329e850d467e7bcc07b2b6bde3752fbda
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52847.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

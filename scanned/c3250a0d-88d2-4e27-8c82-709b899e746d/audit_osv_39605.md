# [H] power: supply: rt9455: Fix use-after-free in power_supply_changed()

## Summary
Severity: High
Advisory: CVE-2026-46270
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46270
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: rt9455: Fix use-after-free in power_supply_changed()

Using the `devm_` variant for requesting IRQ _before_ the `devm_`
variant for allocating/registering the `power_supply` handle, means that
the `power_supply` handle will be deallocated/unregistered _before_ the
interrupt handler (since `devm_` naturally deallocates in reverse
allocation order). This means that during removal, there is a race
condition where an interrupt can fire just _after_ the `power_supply`
handle has been freed, *but* just _before_ the corresponding
unregistration of the IRQ handler has run.

This will lead to the IRQ handler calling `power_supply_changed()` with
a freed `power_supply` handle. Which usually crashes the system or
otherwise silently corrupts the memory...

Note that there is a similar situation which can also happen during
`probe()`; the possibility of an interrupt firing _before_ registering
the `power_supply` handle. This would then lead to the nasty situation
of using the `power_supply` handle *uninitialized* in
`power_supply_changed()`.

Fix this racy use-after-free by making sure the IRQ is requested _after_
the registration of the `power_supply` handle.

## References
- https://git.kernel.org/stable/c/2178dc65d45e2f7bcaa8af8d80d100419bdab251
- https://git.kernel.org/stable/c/62d753b916bd500bb269b7078cdab73198ab4718
- https://git.kernel.org/stable/c/64e15155095f39f4dec9b4659da1238ef8fc54d4
- https://git.kernel.org/stable/c/721449a15170fc5f028a7576d7f65b9f60d53482
- https://git.kernel.org/stable/c/a39f8f06216f73ef40e71e2fe4ad071964c1fd36
- https://git.kernel.org/stable/c/af261f218a7606f93d2c786353d60bb4feb56ef0
- https://git.kernel.org/stable/c/d4e2e3c3caa26b93aa9f36d0a6824b584e2a8dfc
- https://git.kernel.org/stable/c/e2febe375e5ea5afed92f4cd9711bde8f24ee6d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

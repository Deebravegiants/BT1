# [H] serial: 8250: Fix oops for port->pm on uart_change_pm()

## Summary
Severity: High
Advisory: CVE-2023-54220
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54220
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.324, >=4.15.0 <4.19.293, >=4.20.0 <5.4.255, >=5.5.0 <5.10.192, >=5.11.0 <5.15.128, >=5.16.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: 8250: Fix oops for port->pm on uart_change_pm()

Unloading a hardware specific 8250 driver can produce error "Unable to
handle kernel paging request at virtual address" about ten seconds after
unloading the driver. This happens on uart_hangup() calling
uart_change_pm().

Turns out commit 04e82793f068 ("serial: 8250: Reinit port->pm on port
specific driver unbind") was only a partial fix. If the hardware specific
driver has initialized port->pm function, we need to clear port->pm too.
Just reinitializing port->ops does not do this. Otherwise serial8250_pm()
will call port->pm() instead of serial8250_do_pm().

## References
- https://git.kernel.org/stable/c/0c05493341d6f2097f75f0a5dbb7b53a9e8c5f6c
- https://git.kernel.org/stable/c/18e27df4f2b4e257c317ba8076f31a888f6cc64b
- https://git.kernel.org/stable/c/375806616f8c772c33d40e112530887b37c1a816
- https://git.kernel.org/stable/c/66f3e55960698c874b0598277913b478ecd29573
- https://git.kernel.org/stable/c/720a297b334e85d34099e83d1f375b92c3efedd6
- https://git.kernel.org/stable/c/b653289ca6460a6552c8590b75dfa84a0140a46b
- https://git.kernel.org/stable/c/bd70d0b28010d560a8be96b44fea86fe2ba016ae
- https://git.kernel.org/stable/c/dfe2aeb226fd5e19b0ee795f4f6ed8bc494c1534
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54220.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54220
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] ASoC: codecs: simple-mux: Fix enum control bounds check

## Summary
Severity: High
Advisory: CVE-2026-64243
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64243
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: simple-mux: Fix enum control bounds check

simple_mux_control_put() rejects values greater than e->items, but
enum control values are zero based. For the two-entry mux used by this
driver, valid values are 0 and 1, so value 2 must be rejected as well.

Accepting e->items can store an invalid mux state, pass it to the GPIO
setter, and pass it on to the DAPM mux update path where it is used as
an index into the enum text array.

Use the same >= e->items check used by the ASoC enum helpers.

## References
- https://git.kernel.org/stable/c/05ef77f02607a3dc5d7f9762cb990f76843315d4
- https://git.kernel.org/stable/c/164dcbec9632ca93ae313e6da6e4e05584fa0f02
- https://git.kernel.org/stable/c/2ff3ac6f7664fe5639cad01712ac5e021fa7939c
- https://git.kernel.org/stable/c/5fe860af8630cf7c78523cbd68e5a234743585aa
- https://git.kernel.org/stable/c/6fb653b62f169f6050fac45b56bf21ad097e19f6
- https://git.kernel.org/stable/c/d8cc3e747b002a8b965c529de79c0654675b9a1a
- https://git.kernel.org/stable/c/f63ad68e18d774a5d15cd7e405ead63f6b322679
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] can: bcm: validate frame length in bcm_rx_setup() for RTR replies

## Summary
Severity: High
Advisory: CVE-2026-72114
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72114
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: validate frame length in bcm_rx_setup() for RTR replies

bcm_tx_setup() validates cf->len against the CAN/CAN FD DLC limits
before installing frames for TX_SETUP, but bcm_rx_setup() never did
the same for the RTR-reply frame configured via RX_SETUP with
RX_RTR_FRAME.

## References
- https://git.kernel.org/stable/c/1b475c0c72f44622a320a4386ce9e76f85e69bc7
- https://git.kernel.org/stable/c/204f2b232717bc470ddb9e1da1d27dd9c6ef0caa
- https://git.kernel.org/stable/c/59bfddea64159594feb62ef11b7d7a33c8ee3783
- https://git.kernel.org/stable/c/62ec41f364648be79d54d94d0d240ee326948afd
- https://git.kernel.org/stable/c/7d966cdee006911d3957e1a4e72cb93c39cd8c1e
- https://git.kernel.org/stable/c/cc1f9569f1c1adf74fa69d6f716a31b58a2fc6ce
- https://git.kernel.org/stable/c/deb6a697cce3f021e731df543597f37a5e54caab
- https://git.kernel.org/stable/c/e061624c0a86c3c26a2bf017e432fbc93ad68f3a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72114.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

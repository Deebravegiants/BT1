# [H] be2net: Fix buffer overflow in be_get_module_eeprom

## Summary
Severity: High
Advisory: CVE-2022-49581
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49581
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

be2net: Fix buffer overflow in be_get_module_eeprom

be_cmd_read_port_transceiver_data assumes that it is given a buffer that
is at least PAGE_DATA_LEN long, or twice that if the module supports SFF
8472. However, this is not always the case.

Fix this by passing the desired offset and length to
be_cmd_read_port_transceiver_data so that we only copy the bytes once.

## References
- https://git.kernel.org/stable/c/18043da94c023f3ef09c15017bdb04e8f695ef10
- https://git.kernel.org/stable/c/665cbe91de2f7c97c51ca8fce39aae26477c1948
- https://git.kernel.org/stable/c/8ff4f9df73e5c551a72ee6034886c17e8de6596d
- https://git.kernel.org/stable/c/a5a8fc0679a8fd58d47aa2ebcfc5742631f753f9
- https://git.kernel.org/stable/c/a8569f76df7ec5b4b51155c57523a0b356db5741
- https://git.kernel.org/stable/c/aba8ff847f4f927ad7a1a1ee4a9f29989a1a728f
- https://git.kernel.org/stable/c/d7241f679a59cfe27f92cb5c6272cb429fb1f7ec
- https://git.kernel.org/stable/c/fe4473fc7940f14c4a12db873b9729134c212654
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49581.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] staging: rtl8723bs: fix missing shared-key auth challenge length check

## Summary
Severity: High
Advisory: CVE-2026-74649
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74649
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix missing shared-key auth challenge length check

The WEP shared-key authentication handler uses the challenge-text
element's attacker-controlled length without checking it against the
fixed 128-byte chg_txt buffer.

In OnAuthClient() the length from rtw_get_ie() - up to 255 - is used
to perform memcpy() into the 128-byte pmlmeinfo->chg_txt, so a
malicious AP sending a malformed WLAN_EID_CHALLENGE element can
overflow/underfill chg_txt by up to 127 bytes. It is reachable over the
air, before association, during shared-key authentication. In the case
of an overflow, the driver can write out of bounds. In the case of an
underfill, the driver can echo stale buffer memory.

The challenge text is defined to be exactly 128 octets, which is
already provided as the WLAN_AUTH_CHALLENGE_LEN define; require the
element to be exactly that length before use.

## References
- https://git.kernel.org/stable/c/2c56ef658ac8c6bca36bc5574715e8f717207c6c
- https://git.kernel.org/stable/c/39ae1033071001af9bb4573ebdbb43bbbe88f749
- https://git.kernel.org/stable/c/4ba402fd47009d20e51dbfc934abb562098ea35b
- https://git.kernel.org/stable/c/4d018e7d7d908bdfcb5ecfa922b1d5cb9ddb3722
- https://git.kernel.org/stable/c/6235b5156b48ed5d1ce3410d8f0b2fd67d30d944
- https://git.kernel.org/stable/c/87c2f073d2aaea041d531b8e579c47570b54b3b7
- https://git.kernel.org/stable/c/a28a4b0592e4a37ea471bc0d308513a93133ce7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74649.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74649
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

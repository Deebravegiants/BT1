# [C] rxrpc: Fix re-decryption of RESPONSE packets

## Summary
Severity: Critical
Advisory: CVE-2026-45988
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45988
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix re-decryption of RESPONSE packets

If a RESPONSE packet gets a temporary failure during processing, it may end
up in a partially decrypted state - and then get requeued for a retry.

Fix this by just discarding the packet; we will send another CHALLENGE
packet and thereby elicit a further response.  Similarly, discard an
incoming CHALLENGE packet if we get an error whilst generating a RESPONSE;
the server will send another CHALLENGE.

## References
- https://git.kernel.org/stable/c/0422e7a4883f25101903f3e8105c0808aa5f4ce9
- https://git.kernel.org/stable/c/76cb9a2d252274adfae6e293a292434631a7d472
- https://git.kernel.org/stable/c/7b89868305052b94a91b708c462bc2281fa42a4a
- https://git.kernel.org/stable/c/d61482be4aae1835b78875761206241835a7510e
- https://git.kernel.org/stable/c/f55b383070170e988e4dec28be2af1714d258521
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45988.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

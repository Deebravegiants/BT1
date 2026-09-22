# [M] CVE-2024-52917

## Summary
Severity: Medium
Advisory: CVE-2024-52917
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-52917
Type: osv

## Details
Bitcoin Core before 22.0 has a miniupnp infinite loop in which it allocates memory on the basis of random data received over the network, e.g., large M-SEARCH replies from a fake UPnP device.

## References
- https://bitcoincore.org/en/2024/07/31/disclose-upnp-oom/
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52917.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52917

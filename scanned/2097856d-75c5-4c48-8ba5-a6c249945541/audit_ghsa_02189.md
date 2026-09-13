# [H] Data races in rusb

## Summary
Severity: High
Advisory: GHSA-9mxw-4856-9cm5
CVE: CVE-2020-36206
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9mxw-4856-9cm5
Type: github-advisory

## Affected
- crates.io: `rusb` — affected >=0 <0.7.0

## Details
Affected versions of rusb did not require UsbContext to implement Send and Sync. However, through Device and DeviceHandle it is possible to use UsbContexts across threads. This issue allows non-thread safe UsbContext types to be used concurrently leading to data races and memory corruption. The issue was fixed by adding Send and Sync bounds to UsbContext.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36206
- https://github.com/a1ien/rusb/issues/44
- https://github.com/a1ien/rusb
- https://rustsec.org/advisories/RUSTSEC-2020-0098.html

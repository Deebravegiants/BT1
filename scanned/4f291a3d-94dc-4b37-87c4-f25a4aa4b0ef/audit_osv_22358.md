# [H] Use of Externally-Controlled Format String in umlaeute/v4l2loopback

## Summary
Severity: High
Advisory: CVE-2022-2652
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:L)
Published: 2022-08-04
Source: https://osv.dev/vulnerability/CVE-2022-2652
Type: osv

## Details
Depending on the way the format strings in the card label are crafted it's possible to leak kernel stack memory. There is also the possibility for DoS due to the v4l2loopback kernel module crashing when providing the card label on request (reproduce e.g. with many %s modifiers in a row).

## References
- https://huntr.dev/bounties/1b055da5-7a9e-4409-99d7-030280d242d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2652.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2652
- https://github.com/umlaeute/v4l2loopback/commit/e4cd225557486c420f6a34411f98c575effd43dd

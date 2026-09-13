# [H] CVE-2020-8815

## Summary
Severity: High
Advisory: CVE-2020-8815
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-8815
Type: osv

## Details
Improper connection handling in the base connection handler in IKTeam BearFTP before v0.3.1 allows a remote attacker to achieve denial of service via a Slowloris approach by sending a large volume of small packets.

## References
- https://github.com/kolya5544/BearFTP
- https://github.com/kolya5544/BearFTP/releases/tag/0.4.0
- https://github.com/kolya5544/BearFTP/commit/17a6ead72d4a25cbfcef5e27613aa0a5f88a4b26
- https://github.com/kolya5544/BearFTP/commit/66dc9d95e58bca133f265457d32007cdf38b66ad
- https://github.com/kolya5544/BearFTP/blob/f5a8047587c1a96456d4f291c12b038b9ab0d0c5/BearFTP/Program.cs#L503-L525

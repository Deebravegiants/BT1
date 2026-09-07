# [M] UniSharp Laravel Filemanager directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5m2h-7rf2-rpx6
CVE: CVE-2022-40734
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-5m2h-7rf2-rpx6
Type: github-advisory

## Affected
- Packagist: `unisharp/laravel-filemanager` — affected >=0 <2.6.4

## Details
UniSharp laravel-filemanager (aka Laravel Filemanager) with `league/flysystem` version `< 2.0.0` allows download?working_dir=%2F.. directory traversal to read arbitrary files, as exploited in the wild in June 2022.

Since `v2.6.4`, UniSharp laravel-filemanager (aka Laravel Filemanager) requires users to install `league/flysystem` version `>= 2.0.0`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40734
- https://github.com/UniSharp/laravel-filemanager/issues/1150
- https://github.com/UniSharp/laravel-filemanager/issues/1150#issuecomment-1320186966
- https://github.com/UniSharp/laravel-filemanager/issues/1150#issuecomment-1825310417
- https://github.com/UniSharp/laravel-filemanager/commit/8a357d02e8f54ddf130961c64ff2cfc1882bbfcf
- https://github.com/UniSharp/laravel-filemanager

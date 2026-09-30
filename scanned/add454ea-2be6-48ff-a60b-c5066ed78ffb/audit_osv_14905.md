# [M] CVE-2019-12395

## Summary
Severity: Medium
Advisory: CVE-2019-12395
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2019-12395
Type: osv

## Details
In Webbukkit Dynmap 3.0-beta-3 or below, due to a missing login check in servlet/MapStorageHandler.java, an attacker can see a map image without login even if victim enables login-required in setting.

## References
- http://jvn.jp/en/jp/JVN89046645/index.html
- https://github.com/webbukkit/dynmap/issues/2474
- https://github.com/webbukkit/dynmap/commit/641f142cd3ccdcbfb04eda3059be22dd9ed93783
- https://github.com/webbukkit/dynmap/pull/2475

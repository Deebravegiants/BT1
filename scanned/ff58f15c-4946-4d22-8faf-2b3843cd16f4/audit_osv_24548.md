# [M] User uploads proxied from S3 lack `Content-Security-Policy` headers, may be served with `Content-Disposition: inline` in zulip

## Summary
Severity: Medium
Advisory: CVE-2023-22735
Aliases: GHSA-wm83-3764-5wqh
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/CVE-2023-22735
Type: osv

## Details
Zulip is an open-source team collaboration tool. In versions of zulip prior to commit `2f6c5a8` but after commit `04cf68b` users could upload files with arbitrary `Content-Type` which would be served from the Zulip hostname with `Content-Disposition: inline` and no `Content-Security-Policy` header, allowing them to trick other users into executing arbitrary Javascript in the context of the Zulip application.  Among other things, this enables session theft. Only deployments which use the S3 storage (not the local-disk storage) are affected, and only deployments which deployed commit 04cf68b45ebb5c03247a0d6453e35ffc175d55da, which has only been in `main`, not any numbered release. Users affected should upgrade from main again to deploy this fix. Switching from S3 storage to the local-disk storage would nominally mitigate this, but is likely more involved than upgrading to the latest `main` which addresses the issue.

## References
- https://zulip.readthedocs.io/en/latest/production/upgrade-or-modify.html#upgrading-from-a-git-repository
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22735.json
- https://github.com/zulip/zulip/security/advisories/GHSA-wm83-3764-5wqh
- https://nvd.nist.gov/vuln/detail/CVE-2023-22735
- https://github.com/zulip/zulip/commit/04cf68b45ebb5c03247a0d6453e35ffc175d55da
- https://github.com/zulip/zulip/commit/2f6c5a883e106aa82a570d3d1f243993284b70f3

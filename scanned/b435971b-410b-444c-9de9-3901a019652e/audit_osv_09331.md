# [M] CVE-2016-9468

## Summary
Severity: Medium
Advisory: CVE-2016-9468
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-03-28
Source: https://osv.dev/vulnerability/CVE-2016-9468
Type: osv

## Details
Nextcloud Server before 9.0.54 and 10.0.1 & ownCloud Server before 9.0.6 and 9.1.2 suffer from content spoofing in the dav app. The exception message displayed on the DAV endpoints contained partially user-controllable input leading to a potential misrepresentation of information.

## References
- https://github.com/nextcloud/server/commit/7350e13113c8ed484727a5c25331ec11d4d59f5f
- https://github.com/nextcloud/server/commit/a4cfb3ddc1f4cdb585e05c0e9b2f8e52a0e2ee3e
- https://github.com/owncloud/core/commit/96b8afe48570bc70088ccd8f897e9d71997d336e
- https://github.com/owncloud/core/commit/bcc6c39ad8c22a00323a114e9c1a0a834983fb35
- https://nextcloud.com/security/advisory/?id=nc-sa-2016-011
- https://owncloud.org/security/advisory/?id=oc-sa-2016-021
- https://hackerone.com/reports/149798

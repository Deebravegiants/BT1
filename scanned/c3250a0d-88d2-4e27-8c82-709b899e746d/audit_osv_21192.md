# [H] CVE-2021-41137

## Summary
Severity: High
Advisory: CVE-2021-41137
Aliases: GHSA-v64v-g97p-577c
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-13
Source: https://osv.dev/vulnerability/CVE-2021-41137
Type: osv

## Details
Minio is a Kubernetes native application for cloud storage. All users on release `RELEASE.2021-10-10T16-53-30Z` are affected by a vulnerability that involves bypassing policy restrictions on regular users. Normally, checkKeyValid() should return owner true for rootCreds. In the affected version, policy restriction did not work properly for users who did not have service (svc) or security token service (STS) accounts. This issue is fixed in `RELEASE.2021-10-13T00-23-17Z`. A downgrade back to release `RELEASE.2021-10-08T23-58-24Z` is available as a workaround.

## References
- https://github.com/minio/minio/security/advisories/GHSA-v64v-g97p-577c
- https://github.com/minio/minio/commit/415bbc74aacd53a120e54a663e941b1809982dbd
- https://github.com/minio/minio/pull/13388
- https://github.com/minio/minio/pull/13422

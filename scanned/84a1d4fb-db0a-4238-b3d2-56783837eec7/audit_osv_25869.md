# [C] Remote code execution in Squidex

## Summary
Severity: Critical
Advisory: CVE-2023-46253
Aliases: GHSA-phqq-8g7v-3pg5
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/CVE-2023-46253
Type: osv

## Details
Squidex is an open source headless CMS and content management hub. Affected versions are subject to an arbitrary file write vulnerability in the backup restore feature which allows an authenticated attacker to gain remote code execution (RCE). Squidex allows users with the `squidex.admin.restore` permission to create and restore backups. Part of these backups are the assets uploaded to an App. For each asset, the backup zip archive contains a `.asset` file with the actual content of the asset as well as a related `AssetCreatedEventV2` event, which is stored in a JSON file. Amongst other things, the JSON file contains the event type (`AssetCreatedEventV2`), the ID of the asset (`46c05041-9588-4179-b5eb-ddfcd9463e1e`), its filename (`test.txt`), and its file version (`0`). When a backup with this event is restored, the `BackupAssets.ReadAssetAsync` method is responsible for re-creating the asset. For this purpose, it determines the name of the `.asset` file in the zip archive, reads its content, and stores the content in the filestore. When the asset is stored in the filestore via the UploadAsync method, the assetId and fileVersion are passed as arguments. These are further passed to the method GetFileName, which determines the filename where the asset should be stored. The assetId is inserted into the filename without any sanitization and an attacker with squidex.admin.restore privileges to run arbitrary operating system commands on the underlying server (RCE).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46253.json
- https://github.com/Squidex/squidex/security/advisories/GHSA-phqq-8g7v-3pg5
- https://nvd.nist.gov/vuln/detail/CVE-2023-46253

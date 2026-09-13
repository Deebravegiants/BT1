# [M] Mailpit: Thumbnail generation decodes unbounded image dimensions before scaling

## Summary
Severity: Medium
Advisory: CVE-2026-67446
Aliases: GHSA-75mr-qw9x-3r39, GO-2026-6359
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-67446
Type: osv

## Details
Mailpit is an email testing tool and API for developers. Prior to 1.30.4, Mailpit decodes attacker-supplied image attachments into a full raster before checking decoded dimensions, pixel count, or memory use in the GET /api/v1/message/{id}/part/{partID}/thumb endpoint. The Thumbnail handler in server/apiv1/thumbnails.go obtains attachment bytes through storage.GetAttachmentPart(), accepts image/* content, and calls imaging.Decode() with AutoOrientation before imaging.Fill() scales the image to 180 by 120 pixels. A compact image declaring very large dimensions can therefore consume disproportionately large memory and CPU, and opening the message UI can trigger the same endpoint through server/ui-src/components/message/MessageAttachments.vue. This can degrade availability when an unauthenticated client can store the crafted attachment and reach the web API. This issue is fixed in version 1.30.4.

## References
- https://github.com/axllent/mailpit/releases/tag/v1.30.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67446.json
- https://github.com/axllent/mailpit/security/advisories/GHSA-75mr-qw9x-3r39
- https://nvd.nist.gov/vuln/detail/CVE-2026-67446
- https://github.com/axllent/mailpit/commit/6bcb6337838b542d53c348e38c7977f569b6db35

# [M] Secure view can be bypassed by using internal API endpoint in Nextcloud richdocuments

## Summary
Severity: Medium
Advisory: CVE-2023-28645
Aliases: GHSA-95j6-p5cj-5hh5
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/CVE-2023-28645
Type: osv

## Details
Nextcloud richdocuments is a Nextcloud app integrating the office suit Collabora Online. In affected versions the secure view feature of the rich documents app can be bypassed by using unprotected internal API endpoint of the rich documents app. It is recommended that the Nextcloud Office app (richdocuments) is upgraded to 8.0.0-beta.1, 7.0.2 or 6.3.2. Users unable to upgrade may mitigate the issue by taking steps to restrict the ability to download documents. This includes ensuring that the `WOPI configuration` is configured to only serve documents between Nextcloud and Collabora. It is highly recommended to define the list of Collabora server IPs as the allow list within the Office admin settings of Nextcloud.

## References
- https://docs.nextcloud.com/server/latest/admin_manual/office/configuration.html#wopi-settings
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28645.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-95j6-p5cj-5hh5
- https://nvd.nist.gov/vuln/detail/CVE-2023-28645
- https://github.com/nextcloud/richdocuments/pull/2604

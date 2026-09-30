# [M] Metabase subject to Improper Privilege Management

## Summary
Severity: Medium
Advisory: CVE-2023-23629
Aliases: GHSA-ch8f-hhq9-7gv5
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:L)
Published: 2023-01-28
Source: https://osv.dev/vulnerability/CVE-2023-23629
Type: osv

## Details
Metabase is an open source data analytics platform. Affected versions are subject to Improper Privilege Management. As intended, recipients of dashboards subscriptions can view the data as seen by the creator of that subscription. This allows someone with greater access to data to create a dashboard subscription, add people with fewer data privileges, and all recipients of that subscription receive the same data: the charts shown in the email would abide by the privileges of the user who created the subscription. The issue is users with fewer privileges who can view a dashboard are able to add themselves to a dashboard subscription created by someone with additional data privileges, and thus get access to more data via email. This issue is patched in versions 0.43.7.1, 1.43.7.1, 0.44.6.1, 1.44.6.1, 0.45.2.1, and 1.45.2.1. On Metabase instances running Enterprise Edition, admins can disable the "Subscriptions and Alerts" permission for groups that have restricted data permissions, as a workaround.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23629.json
- https://github.com/metabase/metabase/security/advisories/GHSA-ch8f-hhq9-7gv5
- https://nvd.nist.gov/vuln/detail/CVE-2023-23629

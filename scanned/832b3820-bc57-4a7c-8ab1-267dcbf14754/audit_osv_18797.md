# [M] CVE-2020-36192

## Summary
Severity: Medium
Advisory: CVE-2020-36192
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-01-18
Source: https://osv.dev/vulnerability/CVE-2020-36192
Type: osv

## Details
An issue was discovered in the Source Integration plugin before 2.4.1 for MantisBT. An attacker can gain access to the Summary field of private Issues (either marked as Private, or part of a private Project), if they are attached to an existing Changeset. The information is visible on the view.php page, as well as on the list.php page (a pop-up on the Affected Issues id hyperlink). Additionally, if the attacker has "Update threshold" in the plugin's configuration (set to the "updater" access level by default), then they can link any Issue to a Changeset by entering the Issue's Id, even if they do not have access to it.

## References
- https://github.com/mantisbt-plugins/source-integration/issues/344

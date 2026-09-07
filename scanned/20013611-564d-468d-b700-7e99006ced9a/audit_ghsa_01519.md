# [H] Stored XSS in TimelineJS3

## Summary
Severity: High
Advisory: GHSA-2jpm-827p-j44g
CVE: CVE-2020-15092
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-09
Source: https://github.com/advisories/GHSA-2jpm-827p-j44g
Type: github-advisory

## Affected
- npm: `@knight-lab/timelinejs` — affected >=0 <3.7.0

## Details
### Impact
TimelineJS renders some user data as HTML. An attacker could implement an XSS exploit with maliciously crafted content in a number of data fields. This risk is present whether the source data for the timeline is stored on Google Sheets or in a JSON configuration file.

Most TimelineJS users configure their timeline with a Google Sheets document. Those users are exposed to this vulnerability if they grant write access to the document to a malicious inside attacker, if the access of a trusted user is compromised, or if they grant public write access to the document.

Some TimelineJS users configure their timeline with a JSON document. Those users are exposed to this vulnerability if they grant write access to the document to a malicious inside attacker, if the access of a trusted user is compromised, or if write access to the system hosting that document is otherwise compromised.

Although the vulnerability has a [CVSS v3.1 base score of 7.2](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H), this vulnerability has a severity of Moderate due to the likeliness of exploitation.

### Patches
Version 3.7.0 of TimelineJS addresses this in two ways. 

1. For content which is intended to support limited HTML markup for styling and linking, that content is "sanitized" before being added to the DOM.
1. For content intended for simple text display, all markup is stripped. 

Very few users of TimelineJS actually install the TimelineJS code on their server. Most users publish a timeline using a URL hosted on systems we control. The fix for this issue is published to our system such that **those users will automatically begin using the new code**. The only exception would be users who have deliberately edited the embed URL to "pin" their timeline to an earlier version of the code.

Some users of TimelineJS use it as a part of a [wordpress plugin](https://wordpress.org/plugins/knight-lab-timelinejs/). Version 3.7.0.0 of that plugin and newer integrate the updated code. Users are encouraged to update the plugin rather than manually update the embedded version of TimelineJS.

### Workarounds
To exploit this vulnerability, the attacker must have write access to the data source for the Timeline or the server which embeds the timeline.

Thus, the only workaround is appropriate attention to securing write access to the Google Sheet or JSON file which serves as the data source.

### References
For more about the release of TimelineJS which addresses this vulnerability, see the [Knight Lab website](https://knightlab.northwestern.edu/2020/07/09/timelinejs-update/index.html).

A technical write-up of this vulnerability is available [here](https://zanderwork.com/blog/cve-2020-15092/).

### Acknowledgements

This vulnerability was discovered by Zander Work ([@captainGeech42](https://twitter.com/captainGeech42)) of Oregon State University.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [GitHub](https://github.com/NUKnightLab/TimelineJS3/issues)
* File a support request in our [helpdesk system](https://knightlab.zendesk.com/hc/en-us/requests/new)

## References
- https://github.com/NUKnightLab/TimelineJS3/security/advisories/GHSA-2jpm-827p-j44g
- https://nvd.nist.gov/vuln/detail/CVE-2020-15092
- https://knightlab.northwestern.edu/2020/07/09/timelinejs-update/index.html
- https://knightlab.northwestern.edu/posts

# [M] CVE-2021-43827

## Summary
Severity: Medium
Advisory: CVE-2021-43827
Aliases: GHSA-58vr-c56v-qr57
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-12-14
Source: https://osv.dev/vulnerability/CVE-2021-43827
Type: osv

## Details
discourse-footnote is a library providing footnotes for posts in Discourse. ### Impact When posting an inline footnote wrapped in `<a>` tags (e.g. `<a>^[footnote]</a>`, the resulting rendered HTML would include a nested `<a>`, which is stripped by Nokogiri because it is not valid. This then caused a javascript error on topic pages because we were looking for an `<a>` element inside the footnote reference span and getting its ID, and because it did not exist we got a null reference error in javascript. Users are advised to update to version 0.2. As a workaround editing offending posts from the rails console or the database console for self-hosters, or disabling the plugin in the admin panel can mitigate this issue.

## References
- https://github.com/discourse/discourse-footnote/security/advisories/GHSA-58vr-c56v-qr57
- https://github.com/discourse/discourse-footnote/commit/796617e0131277011207541313522cd1946661ab

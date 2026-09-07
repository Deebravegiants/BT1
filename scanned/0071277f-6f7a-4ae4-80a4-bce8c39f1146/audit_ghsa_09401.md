# [H] Apostrophe has stored XSS via javascript: URL in Image Widget Link

## Summary
Severity: High
Advisory: GHSA-5f64-7vfc-rcx6
CVE: CVE-2026-45011
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-5f64-7vfc-rcx6
Type: github-advisory

## Affected
- npm: `apostrophe` — affected 4.29.0

## Details
### Summary
A stored cross-site scripting vulnerability was identified in the image widget functionality. A user with the Editor role can configure an image widget link to use a javascript: URL payload.

Because editors have permission to publish pages, the malicious widget can be published to the live site. When another user, including an administrator or public visitor, clicks the affected image/link, arbitrary JavaScript executes in the victim’s browser.

### Affected Version
ApostropheCMS (tested on version: v4.29.0)

### Steps to Reproduce
**Precondition**
Ensure at least one image exists in the media library.

If the media library is empty:
- Log in as an Editor.
- Open the media library.
- Upload any JPG or PNG image.
- Set any title, for example Probe image.
- Publish the image and close the media manager.

**Exploitation Steps**

- Log in as an Editor.
- Open the home page.
- Enable edit mode for the page.
- In the main content area, click Add content.
- Select the Image widget.
- Choose any existing image from the image picker and save/select it.
- Open the image widget settings.
- Locate the Link to field and change it to URL.
- In the URL field, enter: ```javascript:alert(document.domain)```
<img width="1249" height="979" alt="image" src="https://github.com/user-attachments/assets/c7f77177-1711-461d-b9bd-14292a6996d5" />

- Save the image and click on Update.
- As another user, such as an administrator or guest, open the published page and click the linked image.
- Observe that the JavaScript payload executes.
<img width="1267" height="1034" alt="image" src="https://github.com/user-attachments/assets/a80484b4-873a-47c1-8682-84626523008a" />

**Note**: This attack can also be performed by a Contributor. However, because contributors cannot publish content directly, the malicious image widget remains in the draft version and is only visible to users with access to review drafts, such as administrators or editors.

If an administrator reviews and approves/publishes the affected draft, the stored XSS becomes part of the live page and can then affect all users who interact with the malicious image link.

### Impact
Successful exploitation allows an Editor to store a JavaScript payload in published page content. When a victim clicks the affected image link, the payload executes in the victim’s browser.

This may allow an attacker to:

- perform actions in the context of an authenticated administrator
- access sensitive information available in the CMS interface
- modify page content or configuration
- conduct phishing attacks within the trusted site
- compromise visitors who interact with the published image link

### Recommendation

Validate and sanitize all user-supplied URLs used in widget link fields.

Specifically:

- Reject dangerous URL schemes such as javascript:, data:, and other executable schemes.
- Allow only safe protocols such as http:, https:, mailto:, and relative URLs where appropriate.
- Normalize and validate URLs server-side before storage.
- Encode rendered URLs safely in templates.
- Consider applying a strict Content Security Policy to reduce the impact of XSS.

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-5f64-7vfc-rcx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45011
- https://github.com/apostrophecms/apostrophe
- https://github.com/apostrophecms/apostrophe/releases/tag/apostrophe%404.29.0

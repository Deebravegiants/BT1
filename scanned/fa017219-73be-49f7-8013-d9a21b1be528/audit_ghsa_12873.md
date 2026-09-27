# [M] Path traversal in spotipy

## Summary
Severity: Medium
Advisory: GHSA-q764-g6fm-555v
CVE: CVE-2023-23608
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-01-23
Source: https://github.com/advisories/GHSA-q764-g6fm-555v
Type: github-advisory

## Affected
- PyPI: `spotipy` — affected >=0 <2.22.1

## Details
### Summary
If a malicious URI is passed to the library, the library can be tricked into performing an operation on a different API endpoint than intended.

### Details
The [code Spotipy uses to parse URIs and URLs ](https://github.com/spotipy-dev/spotipy/blob/master/spotipy/client.py#L1942) accepts user data too liberally which allows a malicious user to insert arbitrary characters into the path that is used for API requests. Because it is possible to include `..`, an attacker can redirect for example a track lookup via `spotifyApi.track()` to an arbitrary API endpoint like playlists, but this is possible for other endpoints as well.

Before the security advisory feature was enabled on GitHub, I was already in contact with Stéphane Bruckert via e-mail, and he asked me to look into a potential fix. 

My recommendation is to perform stricter parsing of URLs and URIs, which I implemented in the patch included at the end of the report. If you prefer, I can also invite you to a private fork of the repository.

### Impact
The impact of this vulnerability depends heavily on what operations a client application performs when it handles a URI from a user and how it uses the responses it receives from the API.

## References
- https://github.com/spotipy-dev/spotipy/security/advisories/GHSA-q764-g6fm-555v
- https://nvd.nist.gov/vuln/detail/CVE-2023-23608
- https://github.com/spotipy-dev/spotipy

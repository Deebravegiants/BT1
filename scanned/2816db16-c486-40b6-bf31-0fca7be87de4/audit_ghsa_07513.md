# [M] Mistune: XSS via percent-encoded javascript URI bypass in safe_url()

## Summary
Severity: Medium
Advisory: GHSA-8c25-4j27-2rv3
CVE: CVE-2026-59923
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8c25-4j27-2rv3
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
### Summary
An XSS vulnerability in Mistune allows bypassing of safe_url() protections via percent-encoded javascript URIs.


### Details
The vulnerability exists in HTMLRenderer.safe_url() in Mistune.

The function is intended to block harmful URL schemes such as "javascript:" by checking the prefix of the provided URL:

    _url = url.lower()
    if _url.startswith(self.HARMFUL_PROTOCOLS):
        return "#harmful-link"

However, the input URL is not URL-decoded before this check. Because of this, an attacker can use percent-encoding to bypass the filter. For example:

    javascript%3Aalert(1)

Since "%3A" is not decoded to ":", the check does not detect the "javascript:" scheme.

When rendered in a browser, the URL is decoded, resulting in execution of arbitrary JavaScript upon user interaction.

This effectively bypasses Mistune's built-in safe_url() protection mechanism.



### PoC
1. Install vulnerable version:

    pip install mistune==3.2.0

2. Run the following code:

    import mistune

    markdown = mistune.create_markdown()
    html = markdown("[j](javascript%3Aalert(1))")

    print(html)

3. Output:

    <p><a href="javascript%3Aalert(1)">j</a></p>

4. Open the rendered HTML in a browser and click the link.

5. The browser decodes "%3A" into ":" and executes:

    javascript:alert(1)


### Impact
This is a cross-site scripting (XSS) vulnerability.

An attacker can craft a malicious Markdown link that executes JavaScript in the victim's browser when clicked.

Impact includes:
- Session hijacking (e.g., cookie theft)
- Execution of arbitrary JavaScript in the victim's context
- Potential account takeover depending on the application

This affects any application that renders user-controlled Markdown using Mistune without additional URL sanitization.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-8c25-4j27-2rv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59923
- https://github.com/lepture/mistune/commit/c7101fcbb6e8790e8e39157c5ca2238fc6dd6cbc
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2211.yaml

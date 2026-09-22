# [M] rembg server is vulnerable to Server-Side Request Forgery (SSRF) and a weak default CORS configuration

## Summary
Severity: Medium
Advisory: GHSA-55v6-g8pm-pw4c
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-55v6-g8pm-pw4c
Type: github-advisory

## Affected
- PyPI: `rembg` — affected >=0 <2.0.75

## Details
# GitHub Security Lab (GHSL) Vulnerability Report, rembg: `GHSL-2024-161`, `GHSL-2024-162`

The [GitHub Security Lab](https://securitylab.github.com) team has identified potential security vulnerabilities in [rembg](https://github.com/danielgatis/rembg).

We are committed to working with you to help resolve these issues. In this report you will find everything you need to effectively coordinate a resolution of these issues with the GHSL team.

If at any point you have concerns or questions about this process, please do not hesitate to reach out to us at `securitylab@github.com` (please include `GHSL-2024-161` or `GHSL-2024-162` as a reference). See also [this blog post](https://github.blog/2022-04-22-removing-the-stigma-of-a-cve/) written by GitHub's Advisory Curation team which explains what CVEs and advisories are, why they are important to track vulnerabilities and keep downstream users informed, the CVE assigning process, and how they are used to keep open source software secure.

If you are _NOT_ the correct point of contact for this report, please let us know!

## Summary

rembg server is vulnerable to Server-Side Request Forgery (SSRF) and a weak default CORS configuration, which may allow an attacker website to send requests to servers on the internal network and view image responses.

## Project

rembg

## Tested Version

[v2.0.57](https://github.com/danielgatis/rembg/releases/tag/v2.0.57)

## Details

### Issue 1: SSRF via `/api/remove` (`GHSL-2024-161`)

The [`/api/remove`](https://github.com/danielgatis/rembg/blob/d1e00734f8a996abf512a3a5c251c7a9a392c90a/rembg/commands/s_command.py#L237) endpoint takes a URL query parameter that allows an image to be fetched, processed and returned. An attacker may  be able to query this endpoint to view pictures hosted on the internal network of the rembg server.

```python
 async def get_index(
        url: str = Query(
            default=..., description="URL of the image that has to be processed."
        ),
        commons: CommonQueryParams = Depends(),
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                file = await response.read()
                return await asyncify(im_without_bg)(file, commons)
```

#### Impact

This issue may lead to `Information Disclosure`.

#### Remediation

Ensure that the IP address specified is not a local address. If resolving a domain name, ensure that the resolved IP address is not local.

#### Proof of Concept

`curl -s "http://localhost:7000/api/remove?url=http://0.0.0.0/secret.png" -o output.png`


### Issue 2: CORS misconfiguration (`GHSL-2024-162`)

The following [CORS middleware](https://github.com/danielgatis/rembg/blob/d1e00734f8a996abf512a3a5c251c7a9a392c90a/rembg/commands/s_command.py#L93) is setup incorrectly. All origins are reflected, which allows any website to send cross site requests to the rembg server and thus query any API. Even if authentication were to be enabled, `allow_credentials` is set to True, which would allow any website to send authenticated cross site requests.

```python
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

```

#### Impact

This issue may increase the severity of other vulnerabilities.

#### Remediation

Create an allowlist of specific endpoints that can send cross site requests to the rembg server.

#### Proof of Concept

An attacker website can host the following code:
```javascript
const response = await fetch("http://localhost:7000/api/remove?url=https://0.0.0.0/secret.jpg");
```
If a victim running rembg server were to access the attacker website, the attacker website could read the file `secret.jpg` from the server hosted on the victim's internal network.

## GitHub Security Advisories

We recommend you create a private [GitHub Security Advisory](https://help.github.com/en/github/managing-security-vulnerabilities/creating-a-security-advisory) for these findings. This also allows you to invite the GHSL team to collaborate and further discuss these findings in private before they are [published](https://help.github.com/en/github/managing-security-vulnerabilities/publishing-a-security-advisory).

## Credit

These issues were discovered and reported by GHSL team member [@Kwstubbs (Kevin Stubbings)](https://github.com/Kwstubbs).

## Contact

You can contact the GHSL team at `securitylab@github.com`, please include a reference to `GHSL-2024-161` or `GHSL-2024-162` in any communication regarding these issues.

## Disclosure Policy

This report is subject to a 90-day disclosure deadline, as described in more detail in our [coordinated disclosure policy](https://securitylab.github.com/advisories#policy).

## References
- https://github.com/danielgatis/rembg/security/advisories/GHSA-55v6-g8pm-pw4c
- https://github.com/danielgatis/rembg/commit/07ad0d493057bddf821dcc3e2410eb7e065257c0
- https://github.com/danielgatis/rembg
- https://github.com/danielgatis/rembg/releases/tag/v2.0.75

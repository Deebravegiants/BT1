# [H] Home Assistant does not correctly validate SSL for outgoing requests in core and used libs

## Summary
Severity: High
Advisory: GHSA-m3pm-rpgg-5wj6
CVE: CVE-2025-25305
CWE: CWE-347, CWE-940
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-02-18
Source: https://github.com/advisories/GHSA-m3pm-rpgg-5wj6
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <2024.1.6

## Details
## Summary

Problem: Potential man-in-the-middle attacks due to missing SSL certificate verification in the project codebase and used third-party libraries.

## Details

In the past, `aiohttp-session`/`request` had the parameter `verify_ssl` to control SSL certificate verification. This was a boolean value. In `aiohttp` 3.0, this parameter was deprecated in favor of the `ssl` parameter. Only when `ssl` is set to `None` or provided with a correct configured SSL context the standard SSL certificate verification will happen.

When migrating integrations in Home Assistant and libraries used by Home Assistant, in some cases the `verify_ssl` parameter value was just moved to the new `ssl` parameter. This resulted in these integrations and 3rd party libraries using `request.ssl = True`, which unintentionally turned off SSL certificate verification and opened up a man-in-the-middle attack vector.

Example:
https://github.com/home-assistant/core/blob/c4411914c2e906105b765c00af5740bd0880e946/homeassistant/components/discord/notify.py#L84

When you scan the libraries used by the integrations in Home Assistant, you will find more issues like this.

The general handling in Home Assistant looks good, as `homeassistant.helpers.aoihttp_client._async_get_connector` handles it correctly.

## PoC

1. Check that expired.badssl.com:443 gives an SSL error in when connecting with curl or browser.
2. Add the integration adguard with the setting `host=expired.badssl.com`, `port=443`, `use-ssl=true`, `verify-ssl=true`.
3. Check the logs - you get a HTTP 403 response.

Expected behavior:
1. The integration log shows an `ssl.SSLCertVerificationError`.

The following code shows the problem with `ssl=True`. No exception is raised when `ssl=True` (Python 3.11.6).

```
import asyncio
from ssl import SSLCertVerificationError

import aiohttp

BAD_URL = "https://expired.badssl.com/"


async def run_request(verify_ssl, result_placeholder: str):
    async with aiohttp.ClientSession() as session:
        exception_fired: bool = False
        try:
            await session.request("OPTIONS", BAD_URL, ssl=verify_ssl)
        except SSLCertVerificationError:
            exception_fired = True
        except Exception as error:
            print(error)
        else:
            exception_fired = False
        print(result_placeholder.format(exception_result=exception_fired))


# Case 1: ssl=False --> expected result: No exception
asyncio.run(run_request(False, "Test case 1: expected result: False - result: {exception_result}"))

# Case 2: ssl=None --> expected result: Exception
asyncio.run(run_request(None, "Test case 2: expected result: True - result: {exception_result}"))

# Case 3: ssl=True --> expected result: No Exception
asyncio.run(run_request(True, "Test case 3: expected result: False - result: {exception_result}"))

```

## References
- https://github.com/home-assistant/core/security/advisories/GHSA-m3pm-rpgg-5wj6
- https://nvd.nist.gov/vuln/detail/CVE-2025-25305
- https://github.com/home-assistant/core/commit/8c6547f1b64f4a3d9f10090b97383353c9367892
- https://github.com/home-assistant/core

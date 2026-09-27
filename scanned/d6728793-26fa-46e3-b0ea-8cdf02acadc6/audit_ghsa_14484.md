# [H] Sentry SDK leaks sensitive session information when `sendDefaultPII` is set to `True`

## Summary
Severity: High
Advisory: GHSA-29pr-6jr8-q5jm
CVE: CVE-2023-28117
CWE: CWE-201, CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-03-21
Source: https://github.com/advisories/GHSA-29pr-6jr8-q5jm
Type: github-advisory

## Affected
- PyPI: `sentry-sdk` — affected >=0 <1.14.0

## Details
### Impact

When using the [Django integration](https://docs.sentry.io/platforms/python/guides/django/) of the Sentry SDK in a specific configuration it is possible to leak sensitive cookies values, including the session cookie to Sentry. These sensitive cookies could then be used by someone with access to your Sentry issues to impersonate or escalate their privileges within your application.

The below must be true in order for these sensitive values to be leaked:
1. Your Sentry SDK configuration has `sendDefaultPII` set to `True`
2. You are using a custom name for either of the cookies below in your Django settings.
  - [`SESSION_COOKIE_NAME`](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-SESSION_COOKIE_NAME) or 
  - [`CSRF_COOKIE_NAME`](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-CSRF_COOKIE_NAME) Django settings
3. You are not configured in your organization or project settings to use [our data scrubbing features](https://docs.sentry.io/product/data-management-settings/scrubbing/) to account for the custom cookie names

### Patches
As of version `1.14.0`, the Django integration of the `sentry-sdk` will detect the custom cookie names based on your Django settings and will remove the values from the payload _before_ sending the data to Sentry.

### Workarounds

If you can not update your `sentry-sdk` to a patched version than you can use the SDKs filtering mechanism to remove the cookies from the payload that is sent to Sentry. For error events this can be done with the [before_send](https://docs.sentry.io/platforms/python/configuration/filtering/#using-platformidentifier-namebefore-send-) callback method and for performance related events (transactions) you can use the [before_send_transaction](https://docs.sentry.io/platforms/python/configuration/filtering/#using-platformidentifier-namebefore-send-transaction-) callback method.

If you'd like to handle filtering of these values on the server-side, you can also use our [advanced data scrubbing feature](https://docs.sentry.io/product/data-management-settings/scrubbing/advanced-datascrubbing/) to account for the custom cookie names. Look for the `$http.cookies`, `$http.headers`, `$request.cookies`, or `$request.headers` fields to target with your scrubbing rule.

### References
- [Using Your Tools Against You (Chapter8 Blog Post)](https://medium.com/@tomwolters/using-your-tools-against-you-cea4d2482ebb)
- [Sentry Python SDK Filtering](https://docs.sentry.io/platforms/python/configuration/filtering/)
- [Sentry Data Scrubbing](https://docs.sentry.io/product/data-management-settings/scrubbing/advanced-datascrubbing/)

### Credits
- [Tom Wolters (Chapter8)](https://chapter8.com)

## References
- https://github.com/getsentry/sentry-python/security/advisories/GHSA-29pr-6jr8-q5jm
- https://nvd.nist.gov/vuln/detail/CVE-2023-28117
- https://github.com/getsentry/sentry-python/pull/1842
- https://github.com/getsentry/sentry-python
- https://github.com/getsentry/sentry-python/releases/tag/1.14.0

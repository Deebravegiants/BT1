# [M] Gradio apps vulnerable to timing attacks to guess password

## Summary
Severity: Medium
Advisory: GHSA-hmx6-r76c-85g9
CVE: CVE-2024-1729
CWE: CWE-367
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-hmx6-r76c-85g9
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.19.2

## Details
### Impact
This security policy is with regards to a timing attack that allows users of Gradio apps to potentially guess the password of password-protected Gradio apps. This relies on the fact that string comparisons in Python terminate early, as soon as there is a string mismatch. Because Gradio apps are, by default, not rate-limited, a user could brute-force millions of guesses to figure out the correct username and password.

### Patches
Yes, the problem has been patched in Gradio version 4.19.2 or higher. We have no knowledge of this exploit being used against users of Gradio applications, but we encourage all users to upgrade to Gradio 4.19.2 or higher.

Fixed in: https://github.com/gradio-app/gradio/commit/e329f1fd38935213fe0e73962e8cbd5d3af6e87b

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-hmx6-r76c-85g9
- https://nvd.nist.gov/vuln/detail/CVE-2024-1729
- https://github.com/gradio-app/gradio/commit/e329f1fd38935213fe0e73962e8cbd5d3af6e87b
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/releases/tag/gradio%404.19.2
- https://huntr.com/bounties/f6a10a8d-f538-4cb7-9bb2-85d9f5708124

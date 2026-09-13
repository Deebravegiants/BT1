# [H] dectalk-tts Uses Unencrypted HTTP Request

## Summary
Severity: High
Advisory: GHSA-6cf6-8hvr-r68w
CVE: CVE-2024-31206
CWE: CWE-300, CWE-319, CWE-598
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-6cf6-8hvr-r68w
Type: github-advisory

## Affected
- npm: `dectalk-tts` — affected >=1.0.0 <1.0.1

## Details
### Impact

In `dectalk-tts@1.0.0`, network requests to the third-party API are sent over HTTP, which is unencrypted. Unencrypted traffic can be easily intercepted and modified by attackers. Anyone who uses the package could be the victim of a [man-in-the-middle (MITM)](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) attack.

<ins>Theft</ins>

Because `dectalk-tts` is a text-to-speech package, user requests are expected to only contain natural language. The package [README](https://github.com/JstnMcBrd/dectalk-tts/blob/main/README.md) warns that user input is sent to a third-party API, so users should not send sensitive information regardless.

But if users ignore the warnings and send sensitive information anyway, that information could be stolen by attackers.

<ins>Modification</ins>

Attackers could manipulate requests to the API. However, the worst a modified request could do is return an incorrect audio file or bad request rejection.

Attackers could also manipulate responses from the API, returning malicious output to the user. Output is expected to be a wav-encoded buffer, which users will likely save to a file. This could be a dangerous entrypoint to the user's filesystem.

### Patches

The network request was upgraded to HTTPS in version `1.0.1`. No other changes were made, so updating is risk-free.

### Workarounds

There are no workarounds, but here are some precautions:

- Do not send any sensitive information.

- Carefully verify the API response before saving it.

### References

[Vulnerable code](https://github.com/JstnMcBrd/dectalk-tts/blob/b3e92156cbb699218ac9b9c7d8979abd0e635767/src/index.ts#L18)
[Original report](https://github.com/JstnMcBrd/dectalk-tts/issues/3)
[Patch pull request](https://github.com/JstnMcBrd/dectalk-tts/pull/4)

## References
- https://github.com/JstnMcBrd/dectalk-tts/security/advisories/GHSA-6cf6-8hvr-r68w
- https://nvd.nist.gov/vuln/detail/CVE-2024-31206
- https://github.com/JstnMcBrd/dectalk-tts/issues/3
- https://github.com/JstnMcBrd/dectalk-tts/pull/4
- https://github.com/JstnMcBrd/dectalk-tts/commit/3600d8ac156f27da553ac4ead46d16989a350105
- https://github.com/JstnMcBrd/dectalk-tts
- https://github.com/JstnMcBrd/dectalk-tts/blob/b3e92156cbb699218ac9b9c7d8979abd0e635767/src/index.ts#L18

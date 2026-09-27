# [M] AnythingLLM: Cross-User TTS Audio Disclosure via Chat ID (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2026-42456
Aliases: GHSA-jwqg-jfg3-x5vv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42456
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. Prior to version 1.12.1, GET /api/workspace/:slug/tts/:chatId in AnythingLLM returns the text-to-speech audio for another user's chat response within the same workspace because the route validates workspace membership but does not enforce ownership of the targeted chat row. As a result, an authenticated user can access another user's private assistant response in audio form if the chatId is known or guessed. This constitutes an insecure direct object reference (IDOR) affecting private chat response content exposed through the TTS endpoint. This issue has been patched in version 1.12.1.

## References
- https://github.com/Mintplex-Labs/anything-llm/releases/tag/v1.12.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42456.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-jwqg-jfg3-x5vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42456
- https://github.com/Mintplex-Labs/anything-llm/commit/4f3f77119d342e5489d1ba7533ad6d51bdcd565f

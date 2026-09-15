# [M] Discourse AI Suggestions Contain Insecure Direct Object Reference

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-58055
Aliases: CVE-2025-58055, GHSA-32v2-x274-vfhr
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-discourse-2025-58055
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.5.1

## Details
Discourse is an open-source community discussion platform. In versions 3.5.0 and below, the Discourse AI suggestion endpoints for topic “Title”, “Category”, and “Tags” allowed authenticated users to extract information about topics that they weren’t authorized to access. By modifying the “topic_id” value in API requests to the AI suggestion endpoints, users could target specific restricted topics. The AI model’s responses then disclosed information that the authenticated user couldn’t normally access. This issue is fixed in version 3.5.1. To workaround this issue, users can restrict group access to the AI helper feature through the "composer_ai_helper_allowed_groups" and "post_ai_helper_allowed_groups" site settings.

## References
- https://github.com/discourse/discourse/commit/28d569cae9b33cd55d647bf41806106e33d975c9
- https://github.com/discourse/discourse/security/advisories/GHSA-32v2-x274-vfhr
- https://nvd.nist.gov/vuln/detail/CVE-2025-58055
- https://www.vicarius.io/vsociety/posts/cve-2025-58055-detect-discourse-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-58055-mitigate-discourse-vulnerability

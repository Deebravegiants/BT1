# [H] CVE-2025-4962

## Summary
Severity: High
Advisory: CVE-2025-4962
CVSS: 7.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2025-08-18
Source: https://osv.dev/vulnerability/CVE-2025-4962
Type: osv

## Details
An Insecure Direct Object Reference (IDOR) vulnerability was identified in the `POST /v1/templates` endpoint of the Lunary API, affecting versions up to 0.8.8. This vulnerability allows authenticated users to create templates in another user's project by altering the `projectId` query parameter. The root cause of this issue is the absence of server-side validation to ensure that the authenticated user owns the specified `projectId`. The vulnerability has been addressed in version 1.9.23.

## References
- https://huntr.com/bounties/137a0aef-e243-49d4-832f-8e56056cba1a
- https://github.com/lunary-ai/lunary/commit/e977d06f18a615963ffbe07e5bdff70218c29907

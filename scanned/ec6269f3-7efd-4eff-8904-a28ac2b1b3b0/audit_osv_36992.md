# [C] Budibase Vulnerable to Remote Code Execution via Unsafe eval() in View Filter Map Function (Budibase Cloud)

## Summary
Severity: Critical
Advisory: CVE-2026-27702
Aliases: GHSA-rvhr-26g4-p2r8
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27702
Type: osv

## Details
Budibase is a low code platform for creating internal tools, workflows, and admin panels. Prior to version 3.30.4, an unsafe `eval()` vulnerability in Budibase's view filtering implementation allows any authenticated user (including free tier accounts) to execute arbitrary JavaScript code on the server. This vulnerability ONLY affects Budibase Cloud (SaaS) - self-hosted deployments use native CouchDB views and are not vulnerable. The vulnerability exists in `packages/server/src/db/inMemoryView.ts` where user-controlled view map functions are directly evaluated without sanitization. The primary impact comes from what lives inside the pod's environment: the `app-service` pod runs with secrets baked into its environment variables, including `INTERNAL_API_KEY`, `JWT_SECRET`, CouchDB admin credentials, AWS keys, and more. Using the extracted CouchDB credentials, we verified direct database access, enumerated all tenant databases, and confirmed that user records (email addresses) are readable. Version 3.30.4 contains a patch.

## References
- https://github.com/Budibase/budibase/releases/tag/3.30.4
- https://github.com/Budibase/budibase/security/advisories/GHSA-rvhr-26g4-p2r8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27702.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27702
- https://github.com/Budibase/budibase/commit/348659810cf930dda5f669e782706594c547115d
- https://github.com/Budibase/budibase/pull/18087

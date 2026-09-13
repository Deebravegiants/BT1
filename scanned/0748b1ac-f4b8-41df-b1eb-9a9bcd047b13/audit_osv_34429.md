# [H] Apache bRPC: Stack Exhaustion via Unbounded Recursion in JSON Parser

## Summary
Severity: High
Advisory: CVE-2025-59789
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/CVE-2025-59789
Type: osv

## Details
Uncontrolled recursion in the json2pb component in Apache bRPC (version < 1.15.0) on all platforms allows remote attackers to make the server crash via sending deep recursive json data.

Root Cause:
The bRPC json2pb component uses rapidjson to parse json data from the network. The rapidjson parser uses a recursive parsing method by default. If the input json has a large depth of recursive structure, the parser function may run into stack overflow.

Affected Scenarios:
Use bRPC server with protobuf message to serve http+json requests from untrusted network. Or directly use JsonToProtoMessage to convert json from untrusted input.



How to Fix: 
(Choose one of the following options) 
1. Upgrade bRPC to version 1.15.0, which fixes this issue.
2. Apply this patch:  https://github.com/apache/brpc/pull/3099 



Note:
No matter which option 

you choose, you should know that the fix introduces a recursion depth limit with default value 100. It affects these functions: 

ProtoMessageToJson, ProtoMessageToProtoJson, JsonToProtoMessage, and ProtoJsonToProtoMessage.

 If your requests contain json or protobuf messages that have a depth exceeding the limit, the request will be failed after applying the fix. You can modify the gflag json2pb_max_recursion_depth to change the limit.

## References
- http://www.openwall.com/lists/oss-security/2025/12/01/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59789.json
- https://lists.apache.org/thread/ozmcsztcpxn61jxod8jo8q46jo0oc1zx
- https://nvd.nist.gov/vuln/detail/CVE-2025-59789

# [H] Open WebUI's Insecure Message Access Breaks Authorization

## Summary
Severity: High
Advisory: GHSA-jxwr-g6r6-j3fx
CVE: CVE-2026-44569
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-jxwr-g6r6-j3fx
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.6.19

## Details
### Description

There's an IDOR in the channels message management system that allows authenticated users to modify or delete any message within channels they have read access to. The vulnerability exists in the message update and delete endpoints, which implement channel-level authorization but completely lack message ownership validation.

While the frontend correctly implements ownership checks (showing edit/delete buttons only for message owners or admins), the backend APIs bypass these protections by only validating channel access permissions without verifying that the requesting user owns the target message. This creates a client-side security control bypass where attackers can directly call the APIs to modify other users' messages.

The vulnerability affects both message content modification and deletion, allowing users to tamper with message integrity and audit trails in collaborative channel environments.

### Source - Sink Analysis

**Source:** User-controlled `message_id` parameter in URL path

**Call Chain:**
1. FastAPI route handlers `update_message_by_id()` (line 450) and `delete_message_by_id()` (line 630) in `backend/open_webui/routers/channels.py`
2. Channel-level authorization check: `has_access(user.id, type="read", access_control=channel.access_control)` at lines 457 and 637
3. Message retrieval: `Messages.get_message_by_id(message_id)` at lines 467 and 647  
4. Channel ID validation: `if message.channel_id != id:` at lines 472 and 652
5. **Missing:** Message ownership validation (`message.user_id == user.id`)
6. **Sink:** `Messages.update_message_by_id(message_id, form_data)` at line 476 or `Messages.delete_message_by_id(message_id)` at line 658 - modifies any message without ownership verification

### Proof of Concept

1. Deploy Open WebUI with channels enabled (`ENABLE_CHANNELS=true`)
2. Create scenario:
   - User A creates a channel and grants User B read access
   - User A posts a message in the channel
   - User B observes the message_id from the frontend
3. Exploit: User B sends direct API requests bypassing frontend controls:

Message Update:
```bash
curl -X POST "http://localhost:8080/api/v1/channels/{channel_id}/messages/{victim_message_id}/update" \
     -H "Authorization: Bearer {attacker_token}" \
     -H "Content-Type: application/json" \
     -d '{"content": "Malicious content injected by attacker"}'
```

Message Deletion:
```bash
curl -X DELETE "http://localhost:8080/api/v1/channels/{channel_id}/messages/{victim_message_id}/delete" \
     -H "Authorization: Bearer {attacker_token}"
```

4. Result: Victim's message is modified or deleted despite User B only having read permissions

### Impact

- Users can modify other users' message content within shared channels
- Read-only users gain write/delete capabilities over other users' content

### Remediation

Implement proper message ownership validation in the update and delete endpoints by adding ownership checks that follow the established security pattern used throughout the codebase. First, add a validation condition after the existing message retrieval to ensure only message owners or admins can modify messages: `if user.role != "admin" and message.user_id != user.id and not has_access(user.id, type="write", access_control=channel.access_control)` then raise a 403 Forbidden exception. Second, change the existing permission check from `type="read"` to `type="write"` for both update and delete operations to align with the access control model used in other routers (notes, prompts, knowledge, etc.).

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jxwr-g6r6-j3fx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44569
- https://github.com/open-webui/open-webui

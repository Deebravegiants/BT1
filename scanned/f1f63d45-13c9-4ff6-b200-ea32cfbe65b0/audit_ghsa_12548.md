# [H] DataEase API interface has IDOR vulnerability

## Summary
Severity: High
Advisory: GHSA-7hv6-gv38-78wj
CVE: CVE-2023-32310
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-06-02
Source: https://github.com/advisories/GHSA-7hv6-gv38-78wj
Type: github-advisory

## Affected
- Maven: `io.dataease:dataease-plugin-common` — affected >=0 <1.18.7

## Details
### Impact
The api interface for DataEase delete dashboard and delete system messages is vulnerable to IDOR.

The interface to delete the dashboard:
1. Create two users: user1 and user2
2. User1 creates a dashboard named pan1
3. User2 creates a dashboard named pan2
4. Both user1 and user2 share their dashboards with the demo user
5. User1 wants to delete his dashboard. We hijack the request with burpsuite. The request will probably look like this: POST /api/share/removePanelShares/440efa7f-efd8-11ed-bec7-1144724bc08c HTTP/1.1. 440efa7f-efd8-11ed-bec7-1144724bc08c is the ID of pan1
6. We replace this ID with the ID of pan2 and continue the execution (i.e. we delete the shares of others)
7. Successfully remove the shared link
![image](https://user-images.githubusercontent.com/985347/238271028-d23a9ca3-cd77-42a2-9199-a28ef03f5bf0.png)

The interface to delete system messages:
1. Our request to delete a message is shown below
![image](https://user-images.githubusercontent.com/985347/238271474-1bf6be85-7a39-436d-b209-ac88bf52b591.png)
2. We can delete all messages by simply enumerating the message ID, regardless of whether the message belongs to the requester or not.
3. The interface for marking read messages is also affected

Affected versions: <= 1.18.6

### Patches
The vulnerability has been fixed in v1.18.7.

### Workarounds
It is recommended to upgrade the version to v1.18.7.

### References
If you have any questions or comments about this advisory:

Open an issue in https://github.com/dataease/dataease
Email us at [wei@fit2cloud.com](mailto:wei@fit2cloud.com)

## References
- https://github.com/dataease/dataease/security/advisories/GHSA-7hv6-gv38-78wj
- https://nvd.nist.gov/vuln/detail/CVE-2023-32310
- https://github.com/dataease/dataease/pull/5342
- https://github.com/dataease/dataease/commit/72f428e87b5395c03d2f94ef6185fc247ddbc8dc
- https://github.com/dataease/dataease
- https://github.com/dataease/dataease/releases/tag/v1.18.7

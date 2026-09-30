# [M] Improper Access Control in Onionshare

## Summary
Severity: Medium
Advisory: GHSA-gjj5-998g-v36v
CVE: CVE-2022-21692
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-gjj5-998g-v36v
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=2.3 <2.5

## Details
Between September 26, 2021 and October 8, 2021, [Radically Open Security](https://www.radicallyopensecurity.com/) conducted a penetration test of OnionShare 2.4, funded by the Open Technology Fund's [Red Team lab](https://www.opentech.fund/labs/red-team-lab/). This is an issue from that penetration test.

- Vulnerability ID: OTF-003
- Vulnerability type: Improper Access Control
- Threat level: Moderate

## Description:

Anyone with access to the chat environment can write messages disguised as another chat participant.

## Technical description:

Prerequisites:

- Alice and Bob are legitimate users
- A third user has access to the chat environment

![otf-003-a](https://user-images.githubusercontent.com/156128/140665707-1ecc897e-d33b-4f5b-b585-eb4475c1599f.png)

This screenshot shows Alice (`glimpse-depress`) and Bob (`blinker-doorpost`) joined a chatroom and are the only participants in the chatroom. Then the non-listed user squad-nursing writes a message in the chatroom without being visible in the list of users. The sending of the message itself is not required but was done here to show the initial access. The non-listed participant now renames himself to Bob and writes another message, seemingly coming from Bob.

This can be reproduced by slightly modifying the client-side JavaScript. The `joined` emit needs to be removed from the `socket.on(connect) `event handler. Therefore a client is not listed in the userlist and has no active session.

https://github.com/onionshare/onionshare/blob/d08d5f0f32f755f504494d80794886f346fbafdb/cli/onionshare_cli/resources/static/js/chat.js#L16-L18

This can be done either via a crafted client or runtime modification of the `chat.js` script in the browser's internal debugger.

It is still possible to call the text method and send text to the chat via websocket.

https://github.com/onionshare/onionshare/blob/d08d5f0f32f755f504494d80794886f346fbafdb/cli/onionshare_cli/web/chat_mode.py#L131-L139

It is also possible to call the `update_username` function and choose an existing username from the chat.

https://github.com/onionshare/onionshare/blob/d08d5f0f32f755f504494d80794886f346fbafdb/cli/onionshare_cli/web/chat_mode.py#L141-L162

Afterwards the hidden user can send messages that are displayed as coming from the impersonated user. There is no way to distinguish between the fake and original message.

## Impact:

An adversary with access to the chat environment can impersonate existing chat participants and write messages but not read the conversation. The similar exploit described in OTF-004 (page 19) has only slightly more requirements but also allows for reading.

## Recommendation:

- Implement proper session handling

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-gjj5-998g-v36v
- https://nvd.nist.gov/vuln/detail/CVE-2022-21692
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.5
- https://github.com/pypa/advisory-database/tree/main/vulns/onionshare-cli/PYSEC-2022-43.yaml

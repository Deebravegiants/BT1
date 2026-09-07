# [C] Pre-Auth Blind NoSQL Injection leading to Remote Code Execution

## Summary
Severity: Critical (CVSS 9.8)
Program: Rocket.Chat
Weakness: N/A
Reporter: sonarsource
State: resolved
Disclosed: 2021-05-18T20:36:02.110Z
CVE: CVE-2021-22911
Source: https://hackerone.com/reports/1130721

## Details
**Summary:**
The `getPasswordPolicy` method is vulnerable to NoSQL injection attacks and does not require authentication/authorization. It can be used to take over accounts by leaking password reset tokens. Taking over an admin account leads to Remote Code Execution.

**Description:**
The `getPasswordPolicy` method does not properly validate or sanitize the `token` parameter and can thus be used to perform a blind NoSQL injection. It can be called without authentication (which seems intended), e.g. by using the `/api/v1/method.callAnon` API endpoint

By using [MongoDB's `$regex` operator](https://docs.mongodb.com/manual/reference/operator/query/regex/), a password reset token can be leaked character by character. Example: in order to check if the password reset token begins with a specific letter, e.g. `A`, the attacker would send the JSON object `{"$regex":"^A"}` as the `token` parameter. The response contains the server's password policy when the guess was correct, or an error otherwise. This can be repeated for all possible characters and for each position in the token, until the whole token is known. See the `pwpolicy_leak_token` function in the attached exploit for an implementation of this.

In order to take over an account, an attacker would perform the following high-level steps:
1. Request a password reset for the target user's account. This requires the attacker to know the target user's email address.
1. Leak the password reset token as explained above
1. Reset the target user's password to an attacker known one using the password reset token. The target user cannot have email or TOTP 2FA enabled in order for this step to work.

To gain Remote Code Execution capabilities on the server, an attacker can follow these steps to take over an admin account. The attacker can then use the newly gained admin privileges to create an incoming web hook that has a script. This allows them  to get execute commands or get a shell on the server, because the script is executed on the server without a security boundary in place (which seems to be intended).

See `pre_auth_nosqli.py` for a reference exploit and the attached video for a demonstration of it.

The vulnerable code can be found here: [getPasswordPolicy.js:8](https://github.com/RocketChat/Rocket.Chat/blob/eba1e9b3146e5102baed000953c2cb51930c345c/server/methods/getPasswordPolicy.js#L8)

## Releases Affected:
- Tested on 3.12.1
- Seems to be affected since 3.8.0 as the vulnerability was introduced in [commit b950f17](https://github.com/RocketChat/Rocket.Chat/commit/b950f17e4225efb99b7b80022877f9b2cdf14b64?branch=b950f17e4225efb99b7b80022877f9b2cdf14b64#diff-2fc491cc6f1ca015c2e3f7c36ee12f8d7c7e40907257fd5256d3f39e85c12b88R8)

## Steps To Reproduce (from initial installation to vulnerability):
1. Install Python3 (required by the exploit)
1. Install the Python dependencies required by the exploit: `pip3 install requests`
1. Set up an instance of RocketChat 3.12.1, e.g. by cloning the repo and using Docker Compose:
  1. `git clone git@github.com:RocketChat/Rocket.Chat.git`
  1. `cd Rocket.Chat`
  1. `git checkout tags/3.12.1`
  1. `docker-compose up -d`
1. Configure the instance with default settings, remember the admin's email address (e.g. `admin@rocketchat.local`)
1. Disable all 2FA methods on the admin account
1. Run the reference exploit against the instance, provide the admin's email address: `python3 pre_auth_nosqli.py 'http://localhost:3000' 'admin@rocketchat.local'`
1. The exploit should provide an interactive shell on the the server, use it to verify that you can execute commands as the rocketchat user: `whoami`

## Supporting Material/References:
The attached proof-of-concept video shows the setup and exploitation of a fresh Rocket.Chat instance.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1130721_

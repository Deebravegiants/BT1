# [H] Flowise: resetPassword Authentication Bypass Vulnerability

## Summary
Severity: High
Advisory: GHSA-f6hc-c5jr-878p
CVE: CVE-2026-41276
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-f6hc-c5jr-878p
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
ZDI-CAN-28762: Flowise AccountService resetPassword Authentication Bypass Vulnerability

-- ABSTRACT -------------------------------------

Trend Micro's Zero Day Initiative has identified a vulnerability affecting the following products:
Flowise - Flowise

-- VULNERABILITY DETAILS ------------------------
* Version tested:  3.0.12
* Installer file:  hxxps://github.com/FlowiseAI/Flowise
* Platform tested: NA

---

### Analysis

This vulnerability allows remote attackers to bypass authentication on affected installations of FlowiseAI Flowise. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the resetPassword method of the AccountService class. The issue results from improper implementation of the authentication mechanism. An attacker can leverage this vulnerability to change user's passwords and bypass authentication on the system.

### Product information

FlowiseAI Flowise version 3.0.12 (hxxps://github.com/FlowiseAI/Flowise)

### Setup Instructions

```
npm install flowise@3.0.12
npx flowise start
```

### Root Cause Analysis

FlowiseAI Flowise is an open source low-code tool for developers to build customized large language model (LLM) applications and AI agents. It supports integration with various LLMs, data sources, and tools in order to facilitate rapid development and deployment of AI solutions. Flowise offers a web interface with a drag-and-drop editor, as well as an API, through an Express web server accessible over HTTP on port 3000/TCP.

Flowise allows users to reset forgotten passwords using a token emailed to the email address associated with their account. A token is sent to the user's email when a request is made to the "/api/v1/account/forgot-password" endpoint. Users will submit this token along with their new password to the "/api/v1/account/reset-password" endpoint, and if it is submitted within sufficient time (15 minutes by default, or the value of the PASSWORD_RESET_TOKEN_EXPIRY_IN_MINUTES environment variable) the user will be able to change their password.

The resetPassword() method of the AccountService class is responsible for handling such requests. This method will first retrieve the account information of the user based on their email address, which includes the value of the reset token. The method will then check if the reset token provided matches the one stored in the user's account, and that the token hasn't expired, before changing that users password.

However, there is no check performed to ensure that a password reset token has actually been generated for a user account. By default the value of the reset token stored in a users account is null, or an empty string if they've reset their password before. An attacker with knowledge of the user's email address can submit a request to the "/api/v1/account/reset-password" endpoint containing a null or empty string reset token value and reset that user's password to a value of their choosing. The null or empty string reset token value will allow the attacker to pass the reset token check, and they only have to worry about passing the expiry time check. By default the expiry time stored in the account of a user that has never generated a reset token before is equal to the time of their accounts creation plus 15 minutes (or the value of the PASSWORD_RESET_TOKEN_EXPIRY_IN_MINUTES environment variable).

This means that an attacker with knowledge of a recently created user account's email can change the user's password and use the changed password to bypass authentication.

comments documenting the issue have been added to the following code snippet. Added comments are prepended with "!!!".
From packages/server/src/enterprise/services/account.service.ts
```ts
    public async resetPassword(data: AccountDTO) {
        data = this.initializeAccountDTO(data) 
        const queryRunner = this.dataSource.createQueryRunner()
        await queryRunner.connect()
        try {
            const user = await this.userService.readUserByEmail(data.user.email, queryRunner)  //!!! retrieve stored user info by email address
            if (!user) throw new InternalFlowiseError(StatusCodes.NOT_FOUND, UserErrorMessage.USER_NOT_FOUND)
            //!!!user.tempToken is null or empty string, unless a user has requested a reset token and not used it
            if (user.tempToken !== data.user.tempToken)  //!!! check if the stored token (null by default) matches the provided token
                throw new InternalFlowiseError(StatusCodes.BAD_REQUEST, UserErrorMessage.INVALID_TEMP_TOKEN)

            const tokenExpiry = user.tokenExpiry
            const now = moment()
            const expiryInMins = process.env.PASSWORD_RESET_TOKEN_EXPIRY_IN_MINUTES
                ? parseInt(process.env.PASSWORD_RESET_TOKEN_EXPIRY_IN_MINUTES)
                : 15
            const diff = now.diff(tokenExpiry, 'minutes') //!!! check if token is expired
            if (Math.abs(diff) > expiryInMins) throw new InternalFlowiseError(StatusCodes.BAD_REQUEST, UserErrorMessage.EXPIRED_TEMP_TOKEN)

            // all checks are done, now update the user password, don't forget to hash it and do not forget to clear the temp token
            // leave the user status and other details as is
            //!!! hash and update the user's password since checks passed
            const salt = bcrypt.genSaltSync(parseInt(process.env.PASSWORD_SALT_HASH_ROUNDS || '5'))
            // @ts-ignore
            const hash = bcrypt.hashSync(data.user.password, salt)
            data.user = user
            data.user.credential = hash
            data.user.tempToken = ''  //!!! stored Token value is set to empty string which can also be used by an attacker to bypass the token check
            data.user.tokenExpiry = undefined
            data.user.status = UserStatus.ACTIVE

            await queryRunner.startTransaction()
            data.user = await this.userService.saveUser(data.user, queryRunner)  //!!! save changes to user account
            await queryRunner.commitTransaction()

            // Invalidate all sessions for this user after password reset
            await destroyAllSessionsForUser(user.id as string)
        } catch (error) {
            await queryRunner.rollbackTransaction()
            throw error
        } finally {
            await queryRunner.release()
        }

        return sanitizeUser(data.user)
    }
```

### Proof of Concept

A proof of concept for this vulnerability is provided in ./poc.py. It expects the following syntax:

```
    python3 poc.py --user <USER> --host <HOST> [--port <PORT>] 
```

Where USER is the email address of a user on the server, HOST is the ip address of the vulnerable server, and PORT is the port the vulnerable server is listening on (default: 3000). Options inclosed in square brackets are optional.

In order for this proof of concept to be successful, the user specified as the USER argument must have created their account within the last 15 minutes (or within PASSWORD_RESET_TOKEN_EXPIRY_IN_MINUTES minutes)

By default, the poc will first send a POST request to the "/api/v1/account/reset-password" endpoint of the target server containing a JSON body with a null reset token and the password "TMSR1234!" for the user specified by the USER argument. If the request doesn't successfully change the user's password, the same request will be sent again with the reset token value set to the empty string. Upon successful exploitation, the user's password will be changed to "TMSR1234!".

The provided proof of concept was tested using FlowiseAI Flowise version 3.0.12 runing on a Ubuntu 24.04 VM.

-- CREDIT ---------------------------------------
This vulnerability was discovered by:
Nicholas Zubrisky (@NZubrisky) of TrendAI Research of Trend Micro

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-f6hc-c5jr-878p
- https://nvd.nist.gov/vuln/detail/CVE-2026-41276
- https://github.com/FlowiseAI/Flowise

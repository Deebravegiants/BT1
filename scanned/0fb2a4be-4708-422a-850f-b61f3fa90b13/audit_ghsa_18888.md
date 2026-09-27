# [H] Flowise has Authentication Bypass Using Unprotected Registration Endpoint (/register)

## Summary
Severity: High
Advisory: GHSA-v5w9-prxf-w882
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-v5w9-prxf-w882
Type: github-advisory

## Affected
- npm: `flowise` — affected 3.0.1

## Details
### Summary
An unauthenticated attacker can exploit the unprotected registration endpoint (/register) to create a new user and bypass authentication.
### Details
Critical vulnerability in Flowise 3.0.1 on-premise deployment allows unauthenticated attackers to exploit the /api/v1/account/register endpoint to add a new user and log in using it, enabling authentication bypass.

Meaning that the register functionality is by default open, allowing attackers to create an account and use the api without any restrictions or credentials.

### PoC
A Flowise 3.0.1 instance was deployed via Docker for the purpose of this demonstration.
![1 Docker](https://github.com/user-attachments/assets/fb0b8627-63e3-4523-881f-a0ff6352b678)

After successful deployment the instance setup organization page allows us to register the first account in the system.
![1 newly deployed instance](https://github.com/user-attachments/assets/39d56738-eb97-469e-b96e-61cd7cec64a8)

Creating the first user [research@evasec.io](mailto:research@evasec.io)
![2 configuring account](https://github.com/user-attachments/assets/5fb94b35-c180-4d77-b209-dcff7043c457)

Login to the account
![2 Login](https://github.com/user-attachments/assets/557e8268-099a-4519-bf86-b96a7c5f19ff)

The background request that created the first user to /api/v1/account/register 
![3 request](https://github.com/user-attachments/assets/b74b876d-b784-4142-9d46-10e90ff1b780)

Response
![3 1 response](https://github.com/user-attachments/assets/db769da7-d241-4f0b-a99f-821fa5fdcf05)

We have found that it is possible to reuse the registration request multiple times without any restrictions to create an account and authenticate to the system using it.

Crafting a new request 
{
    "user": {
        "name": "Malicious",
        "email": "attacker@attack.io", 
        "type": "pro",
        "credential": "Password123!"
    }
}
![4 attacker new register](https://github.com/user-attachments/assets/ee34b9f9-7e03-4198-affa-cf2dd2f84666)

Response with 201 code “Created”
![4 1 created](https://github.com/user-attachments/assets/e2a49518-1566-4fe0-9cc5-2a496265974a)

Login using newly created user (attacker)
![5 Login using attacker](https://github.com/user-attachments/assets/b6ef7eb2-d388-469d-92d7-0ca50cdd9873)

Success login
![6 Susccess auth bypass](https://github.com/user-attachments/assets/044376d8-f9c5-4de7-a53c-05dd2c66de83)


An unauthorized user can exploit this vulnerability to register an account and gain access to the Flowise API with authenticated privileges, effectively bypassing authentication. 
### Impact

This is an authentication bypass vulnerability caused by an unprotected registration endpoint (/register).

Users of Flowise 3.0.1(latest) on-premise deployments are impacted. An unauthorized attacker can exploit this vulnerability to register an account after the organization set has been completed, and gain access to the Flowise API with authenticated privileges, effectively bypassing authentication.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-v5w9-prxf-w882
- https://github.com/FlowiseAI/Flowise

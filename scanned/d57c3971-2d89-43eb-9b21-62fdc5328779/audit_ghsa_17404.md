# [M] Grav vulnerable to Information Disclosure via IDOR in Grav Admin Panel

## Summary
Severity: Medium
Advisory: GHSA-4cwq-j7jv-qmwg
CVE: CVE-2025-66306
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-4cwq-j7jv-qmwg
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
## **Summary**

An **IDOR (Insecure Direct Object Reference)** vulnerability in the Grav CMS Admin Panel allows **low-privilege users to access sensitive information** from other accounts.
Although direct account takeover is not possible, **admin email addresses and other metadata can be exposed**, increasing the risk of phishing, credential stuffing, and social engineering.

---

## **Details**

* **Endpoint:** `/admin/accounts/users/{username}`
* **Tested Version:** Grav Admin 1.7.48
* **Affected Accounts:** Authenticated users with **0 privileges** (non-privileged accounts)

**Description:**
Requesting another user’s account details (e.g., `/admin/accounts/users/admin`) as a low-privilege user returns an HTTP **403 Forbidden** response.
However, sensitive information such as the **admin’s email address** is still present in the **response source**, specifically in the `<title>` tag.

**system/src/Grav/Common/Flex/Types/Users/UserCollection.php**
<img width="700" height="327" alt="Screenshot 2025-08-24 021027" src="https://github.com/user-attachments/assets/7e69ae49-d8fc-442f-b00c-9efaec706b2e" />

**system/blueprints/flex/user-accounts.yaml**
<img width="700" height="300" alt="Screenshot 2025-08-24 020521" src="https://github.com/user-attachments/assets/756631c8-d60b-4b84-a08a-2a9c2f81b41f" />


This is a classic **IDOR vulnerability**, where object references (usernames) are not properly protected from unauthorized enumeration.

---

## **PoC**

1. Log in as a **non-privileged user** (0-privilege account).
2. Access another user’s endpoint, for example:

   ```
   GET /admin/accounts/users/admin
   ```
3. Observe the HTTP **403 Forbidden** response.
4. Inspect the **page source**; sensitive data such as the **admin email** can be seen in the `<title>` tag.

**PoC Video:** 

[https://drive.google.com/file/d/1lY_qwqSkN5sPNmHvXGOk6R1mdIgVt71H/view](https://drive.google.com/file/d/1lY_qwqSkN5sPNmHvXGOk6R1mdIgVt71H/view)

---

## **Impact**

* **Type:** Information Disclosure via IDOR
* **Who is impacted:** Low-privilege authenticated users can enumerate other accounts and extract sensitive metadata (admin emails).
* **Risk:** Exposed information can be used for targeted phishing, credential stuffing, brute-force attacks, or social engineering campaigns.
* **Severity Justification:** Only a low-privilege account is required, and sensitive metadata is leaked. Arbitrary code execution is not possible, but the information exposure is **moderate risk**.

---

## **Disclosure & CVE Request**

* We request a **CVE ID** for this vulnerability once validated.
* Please credit the discovery to:

  * **Elvin Nuruyev**
  * **Kanan Farzalili**

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-4cwq-j7jv-qmwg
- https://nvd.nist.gov/vuln/detail/CVE-2025-66306
- https://github.com/getgrav/grav/commit/b7e1958a6e807ac14919447b60e5204a2ea77f62
- https://github.com/getgrav/grav

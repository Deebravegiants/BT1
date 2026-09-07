# [H] Grav vulnerable to Denial of Service via Improper Input Handling in 'Supported' Parameter

## Summary
Severity: High
Advisory: GHSA-m8vh-v6r6-w7p6
CVE: CVE-2025-66305
CWE: CWE-248
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-m8vh-v6r6-w7p6
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
**Endpoint**: `admin/config/system`  
**Submenu**: `Languages`  
**Parameter**: `Supported`  
**Application**: Grav v 1.7.48

---

## Summary

A Denial of Service (DoS) vulnerability was identified in the **"Languages"** submenu of the Grav **admin configuration panel** (`/admin/config/system`). Specifically, the `Supported` parameter fails to properly validate user input. If a malformed value is inserted—such as a single forward slash (`/`) or an XSS test string—it causes a fatal regular expression parsing error on the server.

This leads to application-wide failure due to the use of the `preg_match()` function with an **improperly constructed regular expression**, resulting in the following error:

`preg_match(): Unknown modifier 'o' File: /system/src/Grav/Common/Language/Language.php line 244`

Once triggered, the site becomes completely unavailable to all users.

---

## Details

- **Vulnerable Endpoint**: `POST /admin/config/system`
    
- **Submenu**: `Languages`
    
- **Parameter**: `Supported`  
    

The application dynamically constructs a regular expression using the contents of the `Supported` field without escaping the input using `preg_quote()` or proper validation. This allows attackers to inject invalid syntax into the regex engine, crashing the application during language resolution.

**Stack trace excerpt**:

`Whoops \ Exception \ ErrorException (E_WARNING) preg_match(): Unknown modifier 'o' /system/src/Grav/Common/Language/Language.php244`

---

## Proof of Concept (PoC)

### Payloads:

`/ `

### Steps to Reproduce:

1. Log into the Grav Admin Panel.
    
2. Navigate to: **Configuration** → **System** → **Languages**.
    
3. Locate the `Supported` field.
    
4. Insert one of the payloads above (e.g., a single slash `/`).
    
5. Click **Save**.

<img width="1897" height="639" alt="Pasted image 20250719183223" src="https://github.com/user-attachments/assets/d3a54a20-d30d-46c6-9015-722f80701cfb" />

1. Observe: All pages in the application begin throwing a fatal error and become inaccessible.

<img width="1802" height="998" alt="Pasted image 20250719175229" src="https://github.com/user-attachments/assets/b16750c2-507f-4c30-a9bb-d07fa92bb777" />

---

## Impact

- Application-wide Denial of Service (DoS)
    
- All login and admin views crash with the same error
    
- Potentially exploitable by:
    
    - Admin panel users
        
    - CSRF if misconfigured        
    

---

## References

- **CWE-1333**: Improper Regular Expression
    
- **CWE-20**: Improper Input Validation


## Discoverer

[Marcelo Queiroz](www.linkedin.com/in/marceloqueirozjr) 

by [CVE-Hunters](https://github.com/Sec-Dojo-Cyber-House/cve-hunters)

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-m8vh-v6r6-w7p6
- https://nvd.nist.gov/vuln/detail/CVE-2025-66305
- https://github.com/getgrav/grav/commit/ed640a13143c4177af013cf001969ed2c5e197ee
- https://github.com/getgrav/grav

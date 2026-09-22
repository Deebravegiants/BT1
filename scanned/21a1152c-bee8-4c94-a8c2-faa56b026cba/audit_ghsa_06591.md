# [H] Easy!Appointments Vulnerable to Appointments Takeover via Excessive Data Exposure

## Summary
Severity: High
Advisory: GHSA-4vmm-5qvc-w5p7
CVE: CVE-2026-55651
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-4vmm-5qvc-w5p7
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected 1.5.2

## Details
### Summary
An Excessive Data Exposure vulnerability in the customers search endpoint allows an authenticated user to obtain appointment hashes belonging to other users.
Using these hashes, an attacker can modify or delete appointments of other providers, resulting in an Appointments Takeover.

### Details
The customers search endpoint exposes excessive information, including appointment hashes, to any authenticated user without proper authorization checks.
These hashes uniquely identify appointments that do not belong to the searching user.

By reusing the obtained hashes, an attacker can interact with appointment management endpoints, allowing the modification or deletion of third-party appointments.

The lack of object-level authorization controls leads to an Appointments Takeover, impacting data confidentiality and integrity.

### Impact
This vulnerability allows an authenticated user to take control of appointments belonging to other users. By obtaining and reusing the exposed hashes, an attacker can view, modify, or delete appointments of other providers, compromising data integrity and confidentiality. This may result in unauthorized appointment cancellations or modifications, operational disruption of the service.

### PoC
1. Let's start by viewing an appointment with the provider “Jane Doe.”

<img width="1912" height="880" alt="image" src="https://github.com/user-attachments/assets/57bc0094-6e7f-4ccc-bde4-5604acd1debd" />

2. Now, with the provider “test test” (another provider), let's send the request to /customers/search, where we can verify that the customer “Joe Shmoe” is on the list. This makes it possible to extract the hash of the appointment associated with the user Jane Doe, because the response is returning excessive data.

<img width="579" height="647" alt="image" src="https://github.com/user-attachments/assets/67897f21-d5a6-4edc-bed7-75c23465290b" />

3. With this hash, we then go to the endpoint /calendar/reschedule/{hash} with the provider “test test,” where we can check some information about the appointment.

<img width="1486" height="917" alt="image" src="https://github.com/user-attachments/assets/29b1c20c-e2a8-483e-bd4d-749fb5de497f" />

4. By changing the provider to “test test,” it is possible to change the appointment provider.

<img width="966" height="982" alt="image" src="https://github.com/user-attachments/assets/cfa17cb2-12ac-4034-aae2-1a626d4d0f9c" />

5. By saving, we can verify that the appointment is now in the “test test” provider, thus disappearing from the “John Doe” provider calendar.

Provider "test test" Calendar:

<img width="1916" height="879" alt="image" src="https://github.com/user-attachments/assets/77b9e11a-860f-4c08-847e-fa95c064710d" />

Provider "John Doe" Calendar:

<img width="1917" height="880" alt="image" src="https://github.com/user-attachments/assets/d39566f5-a58c-4337-a781-0886faa83c12" />

5.1. Since we have takeover the appointment, it is possible to cancel/delete it.

<img width="1486" height="736" alt="image" src="https://github.com/user-attachments/assets/2a87b9d0-1726-4fdc-af72-7ae9e20cc050" />

<img width="290" height="867" alt="image" src="https://github.com/user-attachments/assets/815b1df6-dfd4-437a-a2bd-e9b61832d5b0" />

### Recommendation
When making the POST request to the /customers/search endpoint, only return appointments that belong to the provider sending the request. This way, the provider does not have access to the random hash and cannot perform the takeover.

## References
- https://github.com/alextselegidis/easyappointments/security/advisories/GHSA-4vmm-5qvc-w5p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-55651
- https://github.com/alextselegidis/easyappointments/commit/ebbe41130dafa58b0716426c56c8cfd4c22dbceb
- https://github.com/alextselegidis/easyappointments
- https://github.com/alextselegidis/easyappointments/releases/tag/1.6.0

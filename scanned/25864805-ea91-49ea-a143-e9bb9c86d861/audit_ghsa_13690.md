# [M] LibreNMS has Broken Access control on Graphs Feature

## Summary
Severity: Medium
Advisory: GHSA-fpq5-4vwm-78x4
CVE: CVE-2023-48294
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-fpq5-4vwm-78x4
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <23.11.0

## Details
### Summary
This vulnerability occurs when application is not checking access of each type of users as per their role and it autorizing the users to access any feature. When user access his Device dashboard in librenms, one request is going to graph.php to access image of graphs generated on the particular Device. This request can be accessed by lower privileged users as well and they can enumerate devices on librenms with their id or hostname.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

### PoC
1. Login with Lower privilege user
2. Go to /graph.php?width=150&height=45&device=1&type=device_ping_perf&from=1699022192&legend=no&bg=FFFFFF00&popup_title=ICMP+Response
3. If its showing image with "device*ping_perf" which confirms that there is device with id 1
4. Now you can change device parameter in above URL with hostname to check if that Hostname/IP exist or not like
http://127.0.0.1:8000/graph.php?width=150&height=45&device=127.0.0.1&type=device_ping_perf&from=1699022192&legend=no&bg=FFFFFF00&popup_title=ICMP+Response

5. If device hostname doesn't exist then it should show 500 error

Check attached screenshots for more info

Vulnerable code:
https://github.com/librenms/librenms/blob/fa93034edd40c130c2ff00667ca2498d84be6e69/html/graph.php#L19C1-L25C2

Above is vulnerable line of code from Line number 19-25
This is not checking privilege of users to access any device hostname, its just checking if user is authenticated 
or not


### Impact
Low privilege users can see all devices registered by admin users by using this method

### Solution
Implement privilege access control feature to check if low privilege user have access or not.

### Screenshots:-
<img width="967" alt="Screenshot 2023-11-04 at 8 31 15 PM" src="https://user-images.githubusercontent.com/31764504/281085588-1c5d81b9-83d7-4ba8-baf3-03c95a99cefe.png">
<img width="973" alt="Screenshot 2023-11-04 at 8 31 36 PM" src="https://user-images.githubusercontent.com/31764504/281085614-7a4d13b0-d316-4d24-bdd2-05c3a80ffd59.png">
<img width="955" alt="Screenshot 2023-11-04 at 8 31 48 PM" src="https://user-images.githubusercontent.com/31764504/281085629-43aa2b6f-7b18-415f-8001-519bda45f918.png">

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-fpq5-4vwm-78x4
- https://nvd.nist.gov/vuln/detail/CVE-2023-48294
- https://github.com/librenms/librenms/commit/489978a923ed52aa243d3419889ca298a8a6a7cf
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/blob/fa93034edd40c130c2ff00667ca2498d84be6e69/html/graph.php#L19C1-L25C2

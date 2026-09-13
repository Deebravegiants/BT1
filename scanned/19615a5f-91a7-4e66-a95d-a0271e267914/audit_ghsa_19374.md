# [M] Mobile Security Framework (MobSF) Allows Web Server Resource Exhaustion via ZIP of Death Attack

## Summary
Severity: Medium
Advisory: GHSA-c5vg-26p8-q8cr
CVE: CVE-2025-46730
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-c5vg-26p8-q8cr
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0

## Details
**Vulnerable MobSF Versions:** <= v4.3.2

**Details:**
MobSF is a widely adopted mobile application security testing tool used by security teams across numerous organizations. Typically, MobSF is deployed on centralized internal or cloud-based servers that also host other security tools and web applications. Access to the MobSF web interface is often granted to internal security teams, audit teams, and external vendors. 

MobSF provides a feature that allows users to upload ZIP files for static analysis. Upon upload, these ZIP files are automatically extracted and stored within the MobSF directory. However, this functionality lacks a check on the total uncompressed size of the ZIP file, making it vulnerable to a ZIP of Death (zip bomb) attack.

Due to the absence of safeguards against oversized extractions, an attacker can craft a specially prepared ZIP file that is small in compressed form but expands to a massive size upon extraction. Exploiting this, an attacker can exhaust the server's disk space, leading to a complete denial of service (DoS) not just for MobSF, but also for any other applications or websites hosted on the same server.

**Attack Scenario:**
Suppose the server hosting MobSF has 5 GB of free disk space..

A malicious user will first create a genuine hello world application code using android studio and inside this code directory (app//src/main/java/APK_PATH/bomb.txt) he'll place a bomb.txt file. 

This bomb.txt file will have billions of zeros to increase the file size on storage and make it to 4.99 GB. Now suppose the resultant hello world code directory including original code and bomb.txt files will be of 5GB, so the attacker will compress the entire hello world code directory to zip and resultant zip will be around 12-15 MBs only.

An attacker will upload this zip bomb using the MobSF web interface or API. So an attacker will spend only 12-15 MB of his bandwidth. 

Now the MobSF tool will extract that zip file and it'll be automatically converted into its original size 5GB.

So now a web server will be forced to store 5GB of data and its storage will be exhausted by an attacker's single request. 

Web server's storage and resources will not be able to handle other running websites or applications as the storage is exhausted. This way an attacker can achieve complete Web Server Resource Exhaustion. 
 
**Impact:**
1. This vulnerability can lead to complete server disruption in an organization which can affect other internal portals and tools too (which are hosted on the same server).
2. If some organization has created their customised cloud based mobile security tool using MobSF core then an attacker can exploit this vulnerability to crash their servers.

**POC:**
1. Screen Recording :  
https://drive.google.com/file/d/1x7GEPJr2T04Ij5ZFQQtGWvUWXtM4M4aw/view?usp=sharing
2. POC Zip Bomb File (Upon extraction this file will consume 6GB of storage) :  https://drive.google.com/file/d/1N3apL1ySMecnt3HUQcDcuH7hsjPrdwUj/view?usp=sharing

**Mitigation:**
It is recommended to implement a safeguard that checks the total uncompressed size of any uploaded ZIP file before extraction. If the estimated uncompressed size exceeds a safe threshold (e.g., 100 MB), MobSF should reject the file and notify the user.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-c5vg-26p8-q8cr
- https://nvd.nist.gov/vuln/detail/CVE-2025-46730
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/6987a946485a795f4fd38cebdb4860b368a1995d
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
